"""消防设备报废更换 —— 可恢复交接账服务。

交接规则（与业务要求一一对应）：
1. 提交更换单先“预占”新设备：登记新设备 -> 置为 PRE_OCCUPIED -> 记录二维码
   待切换绑定。接管确认前旧设备保持 IN_SERVICE 继续担责。
2. 接管确认后：仅未开始任务(PLANNED)与未关闭隐患转给新设备；旧巡检结果、
   已关闭隐患留在旧设备留档；旧设备置 SCRAPPED，新设备置 IN_SERVICE；
   二维码在同一时刻从旧设备解绑并绑定新设备。
3. 并发：两台终端对同一旧设备提交更换，持全局锁串行，先完成者接管/预占；
   后到的一单保留填写内容并置 CONFLICT，标出冲突单。
4. 写入中断：每完成一个阶段即记入 staged_steps；重试按阶段续作，
   已登记的新设备不重复登记。
5. 旧记录缺少更换关系(PENDING_REVIEW)：补齐关系前不能确认接管。
"""
from datetime import datetime, timezone

from src.db import db, get_lock
from src.db.memory_store import (
    HANDOVER_STEPS,
    DEVICE_IN_SERVICE,
    DEVICE_PRE_OCCUPIED,
    DEVICE_SCRAPPED,
    ORDER_PENDING_REVIEW,
    ORDER_PRE_OCCUPIED,
    ORDER_TAKEN_OVER,
    ORDER_CONFLICT,
    STEP_REGISTER_DEVICE,
)
from src.constants.error_codes import ERROR_CODES
from src.constants.error_messages import ERROR_MESSAGES
from src.utils.errors import HandoverError, HandoverConflictError
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.qr_archive_repository import QrArchiveRepository
from src.repositories.replacement_order_repository import ReplacementOrderRepository
from src.repositories.operation_log_repository import OperationLogRepository
from src.constructors.replacement_order_factory import build_replacement_order_response


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _next_order_no():
    return f"RP-2026-{1000 + ReplacementOrderRepository().next_id()}"


class ReplacementService:
    def __init__(self):
        self.devices = FireDeviceRepository()
        self.tasks = InspectionTaskRepository()
        self.results = InspectionResultRepository()
        self.hazards = HazardTicketRepository()
        self.qrs = QrArchiveRepository()
        self.orders = ReplacementOrderRepository()
        self.logs = OperationLogRepository()

    # ---------- 查询 ----------
    def list_orders(self):
        return [build_replacement_order_response(o) for o in self.orders.find_all()]

    def get_order(self, order_id):
        order = self.orders.find_by_id(order_id)
        if order is None:
            raise HandoverError(
                ERROR_CODES["ORDER_NOT_FOUND"],
                ERROR_MESSAGES["ORDER_NOT_FOUND"].format(order_id=order_id),
                status_code=404,
            )
        return build_replacement_order_response(order)

    def list_logs(self):
        return list(self.logs.find_all())

    # ---------- 提交更换单（预占，可恢复） ----------
    def submit(self, payload: dict, actor: str = "inspector"):
        with get_lock():
            token = (payload.get("client_token") or "").strip()

            # 幂等：同一终端/同一请求令牌重试，直接续作而不是新建单。
            existing = self.orders.find_by_token(token) if token else None
            if existing is not None:
                if existing["status"] == ORDER_CONFLICT:
                    # 冲突草稿必须显式化解后才能重新提交。
                    return build_replacement_order_response(existing)
                return self._resume(existing, actor)

            old_device_id = payload.get("old_device_id")
            old_device = self.devices.find_by_id(old_device_id)
            if old_device is None:
                raise HandoverError(
                    ERROR_CODES["DEVICE_NOT_FOUND"],
                    ERROR_MESSAGES["DEVICE_NOT_FOUND"].format(device_id=old_device_id),
                    status_code=404,
                )

            # 并发门禁优先：旧设备已被另一单接管时，后到的一单一律保留为冲突
            # 草稿（此时旧设备通常已报废，不能再按普通提交报错）。
            conflict = self._conflict_order_for(old_device_id)
            if conflict is not None:
                return self._keep_conflict_draft(payload, conflict, actor)

            # 接管确认前旧设备必须仍在担责。
            if old_device["status"] != DEVICE_IN_SERVICE:
                raise HandoverError(
                    ERROR_CODES["OLD_DEVICE_NOT_SCRAPPABLE"],
                    ERROR_MESSAGES["OLD_DEVICE_NOT_SCRAPPABLE"].format(status=old_device["status"]),
                )

            # 预占前先做输入校验：二维码要么留空、要么当前就绑定在这台旧设备上，
            # 避免预占阶段写到一半才报错留下残单。
            self._validate_new_binding(
                old_device_id,
                (payload.get("new_device_code") or "").strip(),
                (payload.get("qr_code") or "").strip(),
            )

            order = {
                "id": self.orders.next_id(),
                "order_no": _next_order_no(),
                "old_device_id": old_device_id,
                "new_device_id": None,
                "new_device_code": (payload.get("new_device_code") or "").strip(),
                "qr_code": (payload.get("qr_code") or "").strip(),
                "status": ORDER_PRE_OCCUPIED,
                "reason": payload.get("reason", ""),
                "client_token": token,
                "staged_steps": [],
                "conflict_with": None,
                "transferred_task_ids": [],
                "transferred_hazard_ids": [],
                "created_at": _now(),
                "preoccupied_at": "",
                "taken_over_at": "",
                "_payload": dict(payload),
            }
            self.orders.add(order)
            self.logs.append(
                actor, "ReplacementOrder.submit", "ReplacementOrder", order["id"],
                f"提交更换单 {order['order_no']}，旧设备 {old_device['device_code']} 待更换",
                order_id=order["id"], created_at=_now(),
            )
            return self._run_preoccupy_stages(order, actor)

    def _run_preoccupy_stages(self, order: dict, actor: str):
        """按固定阶段推进预占；已完成阶段跳过，保证写入中断后可续作。"""
        payload = order.get("_payload", {})

        # 阶段 1：登记新设备（已登记则复用，绝不重复登记）。
        if STEP_REGISTER_DEVICE not in order["staged_steps"]:
            code = order["new_device_code"]
            new_device = self.devices.find_by_code(code)
            if new_device is None:
                old_device = self.devices.find_by_id(order["old_device_id"])
                new_device = {
                    "id": self.devices.next_id(),
                    "building_id": payload.get("building_id") or old_device["building_id"],
                    "device_code": code,
                    "device_type": payload.get("new_device_type") or old_device["device_type"],
                    "floor": payload.get("floor") or old_device["floor"],
                    "location_desc": payload.get("location_desc") or old_device["location_desc"],
                    "install_date": payload.get("install_date") or _now(),
                    "status": DEVICE_IN_SERVICE,
                    "next_maintenance_at": payload.get("next_maintenance_at") or "",
                }
                self.devices.add(new_device)
                self.logs.append(
                    actor, "FireDevice.create", "FireDevice", new_device["id"],
                    f"登记新设备 {code}（更换单 {order['order_no']}）",
                    order_id=order["id"], created_at=_now(),
                )
            order["new_device_id"] = new_device["id"]
            order["staged_steps"].append(STEP_REGISTER_DEVICE)
            self._maybe_fail(STEP_REGISTER_DEVICE)

        # 阶段 2：预占新设备。若新设备已被别的单预占/接管，则拒绝重复占用。
        if "preoccupy_new_device" not in order["staged_steps"]:
            new_device = self.devices.find_by_id(order["new_device_id"])
            holder = self.orders.find_by_new_device(new_device["id"])
            held_by_other = (
                holder is not None and holder["id"] != order["id"]
                and holder["status"] in (ORDER_PRE_OCCUPIED, ORDER_TAKEN_OVER)
            )
            if held_by_other or new_device["status"] == DEVICE_SCRAPPED:
                if held_by_other:
                    raise HandoverError(
                        ERROR_CODES["NEW_DEVICE_ALREADY_PREOCCUPIED"],
                        ERROR_MESSAGES["NEW_DEVICE_ALREADY_PREOCCUPIED"].format(
                            device_code=new_device["device_code"], order_no=holder["order_no"]),
                        status_code=409,
                    )
                raise HandoverError(
                    ERROR_CODES["OLD_DEVICE_NOT_SCRAPPABLE"],
                    ERROR_MESSAGES["OLD_DEVICE_NOT_SCRAPPABLE"].format(status=DEVICE_SCRAPPED),
                )
            new_device["status"] = DEVICE_PRE_OCCUPIED
            order["status"] = ORDER_PRE_OCCUPIED
            order["preoccupied_at"] = order["preoccupied_at"] or _now()
            order["staged_steps"].append("preoccupy_new_device")
            self.logs.append(
                actor, "FireDevice.status",
                "FireDevice", new_device["id"],
                f"新设备 {new_device['device_code']} 已预占，旧设备暂继续担责",
                order_id=order["id"], created_at=_now(),
            )
            self._maybe_fail("preoccupy_new_device")

        # 阶段 3：记录二维码待切换绑定（同一时刻只绑定一台设备，此处只校验不切换）。
        if "bind_qr_draft" not in order["staged_steps"]:
            qr_code = order.get("qr_code", "")
            if qr_code:
                archive = self.qrs.find_by_code(qr_code)
                if archive is not None and archive["device_id"] != order["old_device_id"]:
                    raise HandoverError(
                        ERROR_CODES["QR_ALREADY_BOUND"],
                        ERROR_MESSAGES["QR_ALREADY_BOUND"].format(
                            qr_code=qr_code, device_id=archive["device_id"]),
                        status_code=409,
                    )
            order["staged_steps"].append("bind_qr_draft")
            self.logs.append(
                actor, "QrArchive.pre_bind", "QrArchive", qr_code or "-",
                f"二维码 {qr_code} 等待接管时切换到新设备",
                order_id=order["id"], created_at=_now(),
            )
            self._maybe_fail("bind_qr_draft")

        return build_replacement_order_response(order)

    def _resume(self, order: dict, actor: str):
        # 再次确认并发门禁：续作期间旧设备可能已被另一单接管。
        conflict = self._conflict_order_for(order["old_device_id"], exclude_id=order["id"])
        if conflict is not None:
            order["status"] = ORDER_CONFLICT
            order["conflict_with"] = conflict["id"]
            self.logs.append(
                actor, "ReplacementOrder.conflict", "ReplacementOrder", order["id"],
                f"续作时发现旧设备已被 {conflict['order_no']} 接管，本单标记冲突",
                order_id=order["id"], created_at=_now(),
            )
            return build_replacement_order_response(order)
        self.logs.append(
            actor, "ReplacementOrder.resume", "ReplacementOrder", order["id"],
            f"从已预占阶段续作：{order['staged_steps']}",
            order_id=order["id"], created_at=_now(),
        )
        return self._run_preoccupy_stages(order, actor)

    # ---------- 接管确认 ----------
    def confirm_takeover(self, order_id: int, actor: str = "supervisor"):
        with get_lock():
            order = self.orders.find_by_id(order_id)
            if order is None:
                raise HandoverError(
                    ERROR_CODES["ORDER_NOT_FOUND"],
                    ERROR_MESSAGES["ORDER_NOT_FOUND"].format(order_id=order_id),
                    status_code=404,
                )
            if order["status"] == ORDER_PENDING_REVIEW:
                raise HandoverError(
                    ERROR_CODES["ORDER_PENDING_REVIEW"],
                    ERROR_MESSAGES["ORDER_PENDING_REVIEW"].format(order_no=order["order_no"]),
                    status_code=409,
                )
            if order["status"] == ORDER_CONFLICT:
                conflict = self.orders.find_by_id(order.get("conflict_with"))
                raise HandoverConflictError(
                    ERROR_CODES["REPLACEMENT_CONFLICT"],
                    ERROR_MESSAGES["REPLACEMENT_CONFLICT"].format(
                        old_device_code=self.devices.find_by_id(order["old_device_id"])["device_code"],
                        order_no=conflict["order_no"] if conflict else "-"),
                    conflict_order_id=order.get("conflict_with"),
                )
            if order["status"] != ORDER_PRE_OCCUPIED or not all(
                s in order["staged_steps"] for s in HANDOVER_STEPS
            ):
                raise HandoverError(
                    ERROR_CODES["ORDER_NOT_PREOCCUPIED"],
                    ERROR_MESSAGES["ORDER_NOT_PREOCCUPIED"].format(order_no=order["order_no"]),
                )

            old_device = self.devices.find_by_id(order["old_device_id"])
            new_device = self.devices.find_by_id(order["new_device_id"])

            # 1) 未开始巡检任务转给新设备。
            transferred_tasks = []
            for task in self.tasks.find_open_tasks_by_device(old_device["id"]):
                self.tasks.reassign(task["id"], new_device["id"])
                transferred_tasks.append(task["id"])
                self.logs.append(
                    actor, "InspectionTask.transfer", "InspectionTask", task["id"],
                    f"未开始任务随接管转移到新设备 {new_device['device_code']}",
                    order_id=order["id"], created_at=_now(),
                )

            # 2) 未关闭隐患转给新设备；已关闭隐患留档。
            transferred_hazards = []
            for ticket in self.hazards.find_open_by_device(old_device["id"]):
                self.hazards.reassign(ticket["id"], new_device["id"])
                transferred_hazards.append(ticket["id"])
                self.logs.append(
                    actor, "HazardTicket.transfer", "HazardTicket", ticket["id"],
                    f"未关闭隐患随接管转移到新设备 {new_device['device_code']}",
                    order_id=order["id"], created_at=_now(),
                )

            # 3) 旧巡检结果、已关闭隐患留档（显式写一条审计说明，不移动数据行）。
            archived_results = self.results.find_by_device(old_device["id"])
            if archived_results:
                self.logs.append(
                    actor, "InspectionResult.archive", "InspectionResult", old_device["id"],
                    f"{len(archived_results)} 条旧巡检结果保留在报废设备 {old_device['device_code']} 档案",
                    order_id=order["id"], created_at=_now(),
                )
            closed = [h for h in self.hazards.find_all()
                      if h.get("device_id") == old_device["id"] and h["rectify_status"] == "CLOSED"]
            if closed:
                self.logs.append(
                    actor, "HazardTicket.archive_closed", "HazardTicket", old_device["id"],
                    f"{len(closed)} 张已关闭隐患留在旧设备 {old_device['device_code']} 档案",
                    order_id=order["id"], created_at=_now(),
                )

            # 4) 设备状态切换：旧报废、新启用（此刻起新设备担责）。
            old_device["status"] = DEVICE_SCRAPPED
            new_device["status"] = DEVICE_IN_SERVICE

            # 5) 二维码同一时刻只绑定一台：从旧设备切到新设备。
            if order.get("qr_code"):
                archive = self.qrs.find_by_code(order["qr_code"])
                if archive is None:
                    # 新贴的码：接管时直接建档绑定新设备。
                    self.qrs.bind_new(order["qr_code"], new_device["id"], _now())
                else:
                    self.qrs.rebind(order["qr_code"], new_device["id"], _now())
                self.logs.append(
                    actor, "QrArchive.rebind", "QrArchive", order["qr_code"],
                    f"二维码 {order['qr_code']} 由旧设备 {old_device['device_code']} 切换绑定到新设备 {new_device['device_code']}",
                    order_id=order["id"], created_at=_now(),
                )

            order["status"] = ORDER_TAKEN_OVER
            order["transferred_task_ids"] = transferred_tasks
            order["transferred_hazard_ids"] = transferred_hazards
            order["taken_over_at"] = _now()
            self.logs.append(
                actor, "ReplacementOrder.takeover", "ReplacementOrder", order["id"],
                (f"接管完成：旧设备 {old_device['device_code']} 报废，新设备 {new_device['device_code']} 担责；"
                 f"转移任务 {transferred_tasks}、隐患 {transferred_hazards}"),
                order_id=order["id"], created_at=_now(),
            )
            return build_replacement_order_response(order)

    # ---------- 旧记录缺更换关系：待核 / 补齐 ----------
    def register_pending_legacy(self, old_device_id: int, reason: str, actor: str = "auditor"):
        """扫描到已报废却没有任何更换单的旧设备时，登记待核单。"""
        with get_lock():
            old_device = self.devices.find_by_id(old_device_id)
            if old_device is None:
                raise HandoverError(
                    ERROR_CODES["DEVICE_NOT_FOUND"],
                    ERROR_MESSAGES["DEVICE_NOT_FOUND"].format(device_id=old_device_id),
                    status_code=404,
                )
            if any(o["old_device_id"] == old_device_id for o in self.orders.find_all()):
                return self.get_order(
                    next(o["id"] for o in self.orders.find_all() if o["old_device_id"] == old_device_id))
            order = {
                "id": self.orders.next_id(),
                "order_no": _next_order_no(),
                "old_device_id": old_device_id,
                "new_device_id": None,
                "new_device_code": "",
                "qr_code": "",
                "status": ORDER_PENDING_REVIEW,
                "reason": reason or "旧记录缺少更换关系，待核",
                "client_token": f"legacy-{old_device_id}",
                "staged_steps": [],
                "conflict_with": None,
                "transferred_task_ids": [],
                "transferred_hazard_ids": [],
                "created_at": _now(),
                "preoccupied_at": "",
                "taken_over_at": "",
                "_payload": {},
            }
            self.orders.add(order)
            self.logs.append(
                actor, "ReplacementOrder.pending_review", "ReplacementOrder", order["id"],
                f"旧设备 {old_device['device_code']} 缺少更换关系，登记待核，补齐前不能接管",
                order_id=order["id"], created_at=_now(),
            )
            return build_replacement_order_response(order)

    def supplement_relation(self, order_id: int, payload: dict, actor: str = "auditor"):
        """为待核单补齐新设备/二维码关系，随后进入正常预占流程。"""
        with get_lock():
            order = self.orders.find_by_id(order_id)
            if order is None:
                raise HandoverError(
                    ERROR_CODES["ORDER_NOT_FOUND"],
                    ERROR_MESSAGES["ORDER_NOT_FOUND"].format(order_id=order_id),
                    status_code=404,
                )
            if order["status"] != ORDER_PENDING_REVIEW:
                raise HandoverError(
                    ERROR_CODES["VALIDATION_FAILED"],
                    f"更换单 {order['order_no']} 当前状态 {order['status']} 无需补齐关系",
                )
            for field in ("new_device_code",):
                if not (payload.get(field) or "").strip():
                    raise HandoverError(
                        ERROR_CODES["RELATION_INCOMPLETE"],
                        ERROR_MESSAGES["RELATION_INCOMPLETE"].format(field=field),
                    )
            qr_code = (payload.get("qr_code") or "").strip()
            self._validate_new_binding(
                order["old_device_id"], payload["new_device_code"].strip(), qr_code)
            order["new_device_code"] = payload["new_device_code"].strip()
            order["qr_code"] = qr_code
            order["reason"] = payload.get("reason", order["reason"])
            order["client_token"] = payload.get("client_token") or f"supplement-{order_id}"
            order["_payload"] = dict(payload)
            self.logs.append(
                actor, "ReplacementOrder.supplement_relation", "ReplacementOrder", order["id"],
                f"待核单 {order['order_no']} 补齐更换关系：新设备 {order['new_device_code']}",
                order_id=order["id"], created_at=_now(),
            )
            # 补齐后先回到预占流程；接管仍需单独确认。
            return self._run_preoccupy_stages(order, actor)

    # ---------- 冲突草稿 ----------
    def _keep_conflict_draft(self, payload: dict, conflict: dict, actor: str):
        old_device = self.devices.find_by_id(payload["old_device_id"])
        draft = {
            "id": self.orders.next_id(),
            "order_no": _next_order_no(),
            "old_device_id": payload["old_device_id"],
            "new_device_id": None,
            "new_device_code": (payload.get("new_device_code") or "").strip(),
            "qr_code": (payload.get("qr_code") or "").strip(),
            "status": ORDER_CONFLICT,
            "reason": payload.get("reason", ""),
            "client_token": payload.get("client_token", ""),
            "staged_steps": [],
            "conflict_with": conflict["id"],
            "transferred_task_ids": [],
            "transferred_hazard_ids": [],
            "created_at": _now(),
            "preoccupied_at": "",
            "taken_over_at": "",
            "_payload": dict(payload),
        }
        self.orders.add(draft)
        self.logs.append(
            actor, "ReplacementOrder.conflict", "ReplacementOrder", draft["id"],
            f"旧设备 {old_device['device_code']} 的更换单 {conflict['order_no']} 已存在，"
            f"本单保留填写并标记冲突",
            order_id=draft["id"], created_at=_now(),
        )
        return build_replacement_order_response(draft)

    def resolve_conflict(self, order_id: int, payload: dict, actor: str = "inspector"):
        """化解冲突草稿：改挂到另一台旧设备后重新走预占流程。"""
        with get_lock():
            order = self.orders.find_by_id(order_id)
            if order is None:
                raise HandoverError(
                    ERROR_CODES["ORDER_NOT_FOUND"],
                    ERROR_MESSAGES["ORDER_NOT_FOUND"].format(order_id=order_id),
                    status_code=404,
                )
            if order["status"] != ORDER_CONFLICT:
                raise HandoverError(
                    ERROR_CODES["VALIDATION_FAILED"],
                    f"更换单 {order['order_no']} 不是冲突草稿",
                )
            new_old_id = payload.get("old_device_id", order["old_device_id"])
            target = self.devices.find_by_id(new_old_id)
            if target is None:
                raise HandoverError(
                    ERROR_CODES["DEVICE_NOT_FOUND"],
                    ERROR_MESSAGES["DEVICE_NOT_FOUND"].format(device_id=new_old_id),
                    status_code=404,
                )
            if target["status"] != DEVICE_IN_SERVICE:
                raise HandoverError(
                    ERROR_CODES["OLD_DEVICE_NOT_SCRAPPABLE"],
                    ERROR_MESSAGES["OLD_DEVICE_NOT_SCRAPPABLE"].format(status=target["status"]),
                )
            conflict = self._takeover_conflict_for(new_old_id, exclude_id=order["id"])
            if conflict is not None:
                order["conflict_with"] = conflict["id"]
                return build_replacement_order_response(order)

            new_code = (payload.get("new_device_code") or order["new_device_code"]).strip()
            qr_code = (payload.get("qr_code") or order.get("qr_code", "")).strip()
            self._validate_new_binding(new_old_id, new_code, qr_code)

            order["old_device_id"] = new_old_id
            order["status"] = ORDER_PRE_OCCUPIED
            order["conflict_with"] = None
            order["new_device_code"] = new_code
            order["qr_code"] = qr_code
            order["staged_steps"] = []
            order["new_device_id"] = None
            order["_payload"] = dict(payload)
            self.logs.append(
                actor, "ReplacementOrder.submit", "ReplacementOrder", order["id"],
                f"冲突草稿 {order['order_no']} 化解，改挂旧设备 {target['device_code']} 重新预占",
                order_id=order["id"], created_at=_now(),
            )
            return self._run_preoccupy_stages(order, actor)

    # ---------- 辅助 ----------
    def _validate_new_binding(self, old_device_id: int, new_device_code: str, qr_code: str):
        if not new_device_code:
            raise HandoverError(
                ERROR_CODES["RELATION_INCOMPLETE"],
                ERROR_MESSAGES["RELATION_INCOMPLETE"].format(field="new_device_code"),
            )
        # 新设备编号若已被别的活跃更换单占用，直接拒绝，禁止两台设备被两张单占用。
        existing = self.devices.find_by_code(new_device_code)
        if existing is not None:
            holder = self.orders.find_by_new_device(existing["id"])
            if holder is not None and holder["status"] in (ORDER_PRE_OCCUPIED, ORDER_TAKEN_OVER):
                raise HandoverError(
                    ERROR_CODES["NEW_DEVICE_ALREADY_PREOCCUPIED"],
                    ERROR_MESSAGES["NEW_DEVICE_ALREADY_PREOCCUPIED"].format(
                        device_code=new_device_code, order_no=holder["order_no"]),
                    status_code=409,
                )
        if qr_code:
            archive = self.qrs.find_by_code(qr_code)
            if archive is not None and archive["device_id"] != old_device_id:
                raise HandoverError(
                    ERROR_CODES["QR_ALREADY_BOUND"],
                    ERROR_MESSAGES["QR_ALREADY_BOUND"].format(
                        qr_code=qr_code, device_id=archive["device_id"]),
                    status_code=409,
                )

    def _takeover_conflict_for(self, old_device_id, exclude_id=None):
        """只有旧设备已被接管才会阻止冲突草稿改挂（预占单尚未担责，允许抢占改挂）。"""
        for order in self.orders.find_active_by_old_device(old_device_id):
            if order["id"] == exclude_id:
                continue
            if order["status"] == ORDER_TAKEN_OVER:
                return order
        return None

    def _conflict_order_for(self, old_device_id, exclude_id=None):
        """旧设备上已存在活跃更换单即构成并发门禁。

        - 已接管(TAKEN_OVER)：硬冲突，后单只能保留为冲突草稿；
        - 已预占(PRE_OCCUPIED)/待核(PENDING_REVIEW)：首次提交已占住旧设备，
          第二份提交同样保留填写并标出首单，避免两张单同时更换同一设备。
        """
        for order in self.orders.find_active_by_old_device(old_device_id):
            if order["id"] == exclude_id:
                continue
            if order["status"] in (ORDER_TAKEN_OVER, ORDER_PRE_OCCUPIED, ORDER_PENDING_REVIEW):
                return order
        return None

    def _maybe_fail(self, stage: str):
        """测试用故障注入：在指定阶段提交落库后中断，验证续作不重复登记。"""
        if db.get("_fail_after_stage") == stage:
            raise RuntimeError(f"simulated write interruption after {stage}")
