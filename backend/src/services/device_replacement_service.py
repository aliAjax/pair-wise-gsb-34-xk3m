import threading

from src.constants.device_status import DeviceStatus
from src.constants.error_messages import ERROR_MESSAGES
from src.constants.handover_step import HandoverStep
from src.constants.log_templates import LOG_TEMPLATES
from src.constants.replacement_status import ReplacementStatus
from src.constructors.device_replacement_factory import create_device_replacement_dto
from src.constructors.fire_device_factory import create_fire_device_dto
from src.repositories.device_replacement_repository import DeviceReplacementRepository
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.repositories.operation_log_repository import OperationLogRepository
from src.utils.formatters import audit_target, utc_now

# 更换单状态（清单见 constants/replacement_status.py）
STATUS_PREOCCUPIED, STATUS_PENDING_REVIEW, STATUS_CONFIRMED, STATUS_CONFLICT = ReplacementStatus
# 设备状态（清单见 constants/device_status.py）
DEVICE_ACTIVE, DEVICE_PREOCCUPIED, DEVICE_RETIRED, DEVICE_RELEASED = DeviceStatus
# 交接步骤（清单见 constants/handover_step.py）：逐步落账，中断后按账续作
(STEP_REGISTER_NEW_DEVICE, STEP_LINK_OPEN_RECORDS, STEP_TRANSFER_TASKS,
 STEP_TRANSFER_HAZARDS, STEP_REBIND_QR, STEP_RETIRE_OLD_DEVICE,
 STEP_ACTIVATE_NEW_DEVICE) = HandoverStep

LOG_SUBMIT, LOG_CONFIRM, LOG_CONFLICT, LOG_PENDING_REVIEW, LOG_BACKFILL, LOG_STEP = LOG_TEMPLATES["DeviceReplacement"]


class ReplacementError(Exception):
    """更换交接业务异常：code 对应 constants/error_codes，消息取自 constants/error_messages。"""

    def __init__(self, code, **context):
        super().__init__(ERROR_MESSAGES[code])
        self.code = code
        self.context = context


class DeviceReplacementService:
    """报废更换交接账：预占新设备 → (待核) → 确认接管 / 冲突标记，全程按步骤落账可恢复。"""

    def __init__(self):
        self.repo = DeviceReplacementRepository()
        self.devices = FireDeviceRepository()
        self.tasks = InspectionTaskRepository()
        self.hazards = HazardTicketRepository()
        self.logs = OperationLogRepository()
        self._lock = threading.Lock()  # 两台终端并发提交/确认时串行化“谁先到账”

    def list(self):
        return self.repo.find_all()

    def logs_of(self, replacement_id):
        order = self.repo.find_by_id(replacement_id)
        if order is None:
            raise ReplacementError("REPLACEMENT_NOT_FOUND", replacement_id=replacement_id)
        return self.logs.find_by_target("DeviceReplacement", order["id"])

    def submit(self, payload):
        request_id = (payload or {}).get("request_id")
        if not request_id:
            raise ReplacementError("VALIDATION_FAILED", field="request_id")
        with self._lock:
            # 写入中断续作：同一 request_id 直接返回已预占的更换单，不重复登记新设备
            existing = self.repo.find_by_request_id(request_id)
            if existing is not None:
                return existing
            old = self.devices.find_by_id(payload.get("old_device_id"))
            if old is None:
                raise ReplacementError("DEVICE_NOT_FOUND", device_id=payload.get("old_device_id"))
            if old.get("status") == DEVICE_RETIRED:
                raise ReplacementError("REPLACEMENT_INVALID_STATE", status=old.get("status"))
            order = create_device_replacement_dto(
                id=self.repo.next_id(),
                request_id=request_id,
                old_device_id=old["id"],
                new_device_id=None,
                status=STATUS_PREOCCUPIED,
                reason=payload.get("reason", ""),
                operator_id=payload.get("operator_id", 1),
                qr_code=old.get("qr_code"),  # 交接账快照：确认接管时凭此换绑二维码
                created_at=utc_now(),
            )
            self.repo.save(order)
            # 旧设备已被他单接管：本单保留填写并直接标冲突，不再预占新设备
            winner = self.repo.find_confirmed_for_device(old["id"], exclude_id=order["id"])
            if winner is not None:
                self._mark_conflict(order, winner)
                return order
            self._run_step(order, STEP_REGISTER_NEW_DEVICE, lambda: self._register_new_device(order, payload, old))
            self._run_step(order, STEP_LINK_OPEN_RECORDS, lambda: self._link_open_records(order))
            self.logs.record(LOG_SUBMIT, "DeviceReplacement", order["id"], audit_target("FireDevice", old["id"]))
            return order

    def confirm(self, replacement_id):
        with self._lock:
            order = self.repo.find_by_id(replacement_id)
            if order is None:
                raise ReplacementError("REPLACEMENT_NOT_FOUND", replacement_id=replacement_id)
            if order["status"] == STATUS_CONFIRMED:
                return order  # 幂等：重复确认直接返回已接管单
            if order["status"] == STATUS_CONFLICT:
                raise ReplacementError("REPLACEMENT_INVALID_STATE", status=order["status"])
            # 两台终端同时提交同一旧设备：首次完成接管者胜，本单保留填写并标冲突
            winner = self.repo.find_confirmed_for_device(order["old_device_id"], exclude_id=order["id"])
            if winner is not None:
                self._mark_conflict(order, winner)
                raise ReplacementError("REPLACEMENT_CONFLICT", winner_id=winner["id"])
            # 旧记录缺少更换关系 → 先待核，补齐前不能确认接管
            orphans = self._orphan_open_records(order)
            if orphans:
                order["status"] = STATUS_PENDING_REVIEW
                order["pending_record_ids"] = orphans
                self.repo.save(order)
                self.logs.record(LOG_PENDING_REVIEW, "DeviceReplacement", order["id"], ",".join(orphans))
                raise ReplacementError("REPLACEMENT_PENDING_REVIEW", pending=orphans)
            self._run_step(order, STEP_TRANSFER_TASKS, lambda: self._transfer_tasks(order))
            self._run_step(order, STEP_TRANSFER_HAZARDS, lambda: self._transfer_hazards(order))
            self._run_step(order, STEP_REBIND_QR, lambda: self._rebind_qr(order))
            self._run_step(order, STEP_RETIRE_OLD_DEVICE, lambda: self._retire_old_device(order))
            self._run_step(order, STEP_ACTIVATE_NEW_DEVICE, lambda: self._activate_new_device(order))
            order["status"] = STATUS_CONFIRMED
            order["confirmed_at"] = utc_now()
            order["pending_record_ids"] = []
            self.repo.save(order)
            # 同一旧设备的其它在途更换单 → 保留填写并标冲突
            for other in self.repo.find_open_for_device(order["old_device_id"], exclude_id=order["id"]):
                self._mark_conflict(other, order)
            self.logs.record(LOG_CONFIRM, "DeviceReplacement", order["id"], audit_target("FireDevice", order["new_device_id"]))
            return order

    def backfill(self, replacement_id):
        with self._lock:
            order = self.repo.find_by_id(replacement_id)
            if order is None:
                raise ReplacementError("REPLACEMENT_NOT_FOUND", replacement_id=replacement_id)
            if order["status"] in (STATUS_CONFIRMED, STATUS_CONFLICT):
                raise ReplacementError("REPLACEMENT_INVALID_STATE", status=order["status"])
            linked = self._link_open_records(order)  # 补齐旧记录的更换关系
            order["pending_record_ids"] = []
            if order["status"] == STATUS_PENDING_REVIEW:
                order["status"] = STATUS_PREOCCUPIED
            self.repo.save(order)
            self.logs.record(LOG_BACKFILL, "DeviceReplacement", order["id"], f"linked={linked}")
            return order

    def _run_step(self, order, step, action):
        # 中断续作：已落账的交接步骤不重复执行
        if step in order["steps_done"]:
            return
        action()
        order["steps_done"].append(step)
        self.repo.save(order)
        self.logs.record(LOG_STEP, "DeviceReplacement", order["id"], step)

    def _register_new_device(self, order, payload, old):
        if order["new_device_id"] is not None:
            return  # 已预占过新设备（中断恢复），跳过不重复登记
        new_device = create_fire_device_dto(
            id=self.devices.next_id(),
            building_id=old["building_id"],
            device_code=payload.get("new_device_code") or f"{old['device_code']}-R{order['id']}",
            device_type=old["device_type"],
            floor=old["floor"],
            location_desc=old["location_desc"],
            install_date=utc_now(),
            status=DEVICE_PREOCCUPIED,  # 预占中：接管确认前旧设备继续担责
            next_maintenance_at=old["next_maintenance_at"],
            qr_code=None,  # 二维码到确认接管时才换绑
        )
        self.devices.save(new_device)
        order["new_device_id"] = new_device["id"]
        self.repo.save(order)

    def _link_open_records(self, order):
        """把旧设备尚未挂接的未开始任务和未关闭隐患挂到本更换单（更换关系）。

        只认领 replacement_id 为空的记录：已被其它在途更换单认领的记录不抢占，
        最终由完成接管的单子统一转交并改挂到自己名下。
        """
        linked = 0
        for task in self.tasks.find_open_by_device(order["old_device_id"]):
            if task.get("replacement_id") is None:
                task["replacement_id"] = order["id"]
                self.tasks.save(task)
                linked += 1
        for hazard in self.hazards.find_open_by_device(order["old_device_id"]):
            if hazard.get("replacement_id") is None:
                hazard["replacement_id"] = order["id"]
                self.hazards.save(hazard)
                linked += 1
        return linked

    def _orphan_open_records(self, order):
        """旧记录缺少更换关系（replacement_id 为空）→ 待核清单。"""
        orphans = []
        for task in self.tasks.find_open_by_device(order["old_device_id"]):
            if task.get("replacement_id") is None:
                orphans.append(audit_target("InspectionTask", task["id"]))
        for hazard in self.hazards.find_open_by_device(order["old_device_id"]):
            if hazard.get("replacement_id") is None:
                orphans.append(audit_target("HazardTicket", hazard["id"]))
        return orphans

    def _transfer_tasks(self, order):
        # 只转未开始任务；进行中/已完成任务留在旧设备留档
        for task in self.tasks.find_open_by_device(order["old_device_id"]):
            task["device_id"] = order["new_device_id"]
            task["replacement_id"] = order["id"]  # 交接账：记录由哪张更换单转交
            self.tasks.save(task)

    def _transfer_hazards(self, order):
        # 只转未关闭隐患；已关闭隐患留在旧设备留档
        for hazard in self.hazards.find_open_by_device(order["old_device_id"]):
            hazard["device_id"] = order["new_device_id"]
            hazard["replacement_id"] = order["id"]  # 交接账：记录由哪张更换单转交
            self.hazards.save(hazard)

    def _rebind_qr(self, order):
        qr_code = order.get("qr_code")
        if not qr_code:
            return
        old = self.devices.find_by_id(order["old_device_id"])
        new = self.devices.find_by_id(order["new_device_id"])
        # 二维码同一时刻只绑定一台设备：先解绑旧设备再绑定新设备
        if old is not None and old.get("qr_code") == qr_code:
            old["qr_code"] = None
            self.devices.save(old)
        if new is not None and new.get("qr_code") != qr_code:
            new["qr_code"] = qr_code
            self.devices.save(new)

    def _retire_old_device(self, order):
        old = self.devices.find_by_id(order["old_device_id"])
        if old is not None and old.get("status") != DEVICE_RETIRED:
            old["status"] = DEVICE_RETIRED
            self.devices.save(old)

    def _activate_new_device(self, order):
        new = self.devices.find_by_id(order["new_device_id"])
        if new is not None and new.get("status") == DEVICE_PREOCCUPIED:
            new["status"] = DEVICE_ACTIVE
            self.devices.save(new)

    def _mark_conflict(self, order, winner):
        order["status"] = STATUS_CONFLICT
        order["conflict_with"] = winner["id"]
        # 释放本单预占的新设备，避免冲突单长期占用
        device = self.devices.find_by_id(order.get("new_device_id"))
        if device is not None and device.get("status") == DEVICE_PREOCCUPIED:
            device["status"] = DEVICE_RELEASED
            self.devices.save(device)
        self.repo.save(order)
        self.logs.record(LOG_CONFLICT, "DeviceReplacement", order["id"], f"winner={winner['id']}")
