"""设备报废更换交接账规则测试（纯标准库，无外部依赖）。

运行：cd backend && python3 -m unittest discover -s tests -v
"""
import sys
import os
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.memory_store import reset_db, db
from src.services.replacement_service import ReplacementService
from src.utils.errors import HandoverError


def submit_payload(**over):
    base = {
        "old_device_id": 1,
        "new_device_code": "HQ-01-001-N",
        "qr_code": "QR-0001",
        "client_token": "tok-1",
        "new_device_type": "HYDRANT",
        "building_id": 1,
        "floor": "1F",
        "location_desc": "大堂新消火栓",
        "reason": "老化报废",
    }
    base.update(over)
    return base


class HandoverTests(unittest.TestCase):
    def setUp(self):
        reset_db()
        self.svc = ReplacementService()

    # 规则 1：预占后、接管前旧设备继续担责
    def test_old_device_keeps_responsibility_until_takeover(self):
        order = self.svc.submit(submit_payload())
        self.assertEqual(order["status"], "PRE_OCCUPIED")
        self.assertEqual(self.svc.devices.find_by_id(1)["status"], "IN_SERVICE")
        self.assertEqual(
            self.svc.devices.find_by_id(order["new_device_id"])["status"], "PRE_OCCUPIED")

    # 规则 2：接管后只转未开始任务、未关闭隐患；历史结果与已关闭隐患留档
    def test_takeover_transfers_only_open_work_and_archives_history(self):
        order = self.svc.submit(submit_payload())
        result = self.svc.confirm_takeover(order["id"])

        self.assertEqual(result["status"], "TAKEN_OVER")
        new_id = order["new_device_id"]
        # PLANNED 任务转移，IN_PROGRESS 任务留在旧设备
        self.assertEqual(self.svc.tasks.find_all()[0]["device_id"], new_id)
        self.assertEqual(self.svc.tasks.find_all()[1]["device_id"], 1)
        # 未关闭隐患转移，已关闭隐患留档
        self.assertEqual(self.svc.hazards.find_all()[0]["device_id"], new_id)
        self.assertEqual(self.svc.hazards.find_all()[1]["device_id"], 2)
        # 旧巡检结果留在旧设备
        self.assertTrue(all(r["device_id"] == 1 for r in self.svc.results.find_by_device(1)))
        # 设备状态切换
        self.assertEqual(self.svc.devices.find_by_id(1)["status"], "SCRAPPED")
        self.assertEqual(self.svc.devices.find_by_id(new_id)["status"], "IN_SERVICE")

    # 规则 2b：二维码同一时刻只绑定一台设备
    def test_qr_switches_atomically_to_new_device(self):
        order = self.svc.submit(submit_payload())
        # 接管前二维码仍在旧设备
        self.assertEqual(self.svc.qrs.find_by_code("QR-0001")["device_id"], 1)
        self.svc.confirm_takeover(order["id"])
        qr = self.svc.qrs.find_by_code("QR-0001")
        self.assertEqual(qr["device_id"], order["new_device_id"])
        self.assertEqual(len(qr["binding_history"]), 2)

    def test_qr_bound_elsewhere_rejected(self):
        with self.assertRaises(HandoverError) as ctx:
            self.svc.submit(submit_payload(qr_code="QR-0002"))
        self.assertEqual(ctx.exception.code, "QR_ALREADY_BOUND")

    # 规则 3：两台终端并发提交同一旧设备，只有一单接管，另一单保留为冲突草稿
    def test_concurrent_submits_single_takeover_and_conflict_draft(self):
        outcomes = {}
        barrier = threading.Barrier(2)

        def worker(token, code):
            svc = ReplacementService()
            barrier.wait()
            order = svc.submit(submit_payload(client_token=token, new_device_code=code, qr_code=""))
            if order["status"] == "PRE_OCCUPIED":
                order = svc.confirm_takeover(order["id"])
            outcomes[token] = order["status"]

        t1 = threading.Thread(target=worker, args=("term-1", "N-1"))
        t2 = threading.Thread(target=worker, args=("term-2", "N-2"))
        t1.start(); t2.start(); t1.join(); t2.join()

        self.assertEqual(sorted(outcomes.values()), ["CONFLICT", "TAKEN_OVER"])
        taken = [o for o in self.svc.orders.find_all() if o["status"] == "TAKEN_OVER"]
        conflicts = [o for o in self.svc.orders.find_all() if o["status"] == "CONFLICT"]
        self.assertEqual(len(taken), 1)
        self.assertEqual(len(conflicts), 1)
        # 冲突草稿保留填写内容并标出冲突单
        self.assertEqual(conflicts[0]["conflict_with"], taken[0]["id"])
        self.assertTrue(conflicts[0]["new_device_code"])

    # 新设备不允许被两张更换单占用
    def test_new_device_cannot_be_occupied_by_two_orders(self):
        order = self.svc.submit(
            submit_payload(client_token="a", new_device_code="DUP-N", qr_code=""))
        self.svc.confirm_takeover(order["id"])
        with self.assertRaises(HandoverError) as ctx:
            self.svc.submit(
                submit_payload(old_device_id=2, client_token="b", new_device_code="DUP-N", qr_code=""))
        self.assertEqual(ctx.exception.code, "NEW_DEVICE_ALREADY_PREOCCUPIED")

    # 规则 4：写入中断后从已预占阶段续作，不重复登记新设备
    def test_resume_after_interruption_does_not_duplicate_device(self):
        for fail_stage in ["register_new_device", "preoccupy_new_device", "bind_qr_draft"]:
            reset_db(fail_after_stage=fail_stage)
            svc = ReplacementService()
            with self.assertRaises(RuntimeError):
                svc.submit(submit_payload(client_token="resume-tok"))
            # 中断后无论新设备是否已登记，编号只出现一次
            db["_fail_after_stage"] = None
            resumed = svc.submit(submit_payload(client_token="resume-tok"))
            count = sum(
                1 for d in svc.devices.find_all() if d["device_code"] == "HQ-01-001-N")
            self.assertEqual(count, 1, f"stage {fail_stage}: duplicate new device")
            # 续作只产生一张更换单
            self.assertEqual(
                len([o for o in svc.orders.find_all() if o.get("client_token") == "resume-tok"]), 1)
            taken = svc.confirm_takeover(resumed["id"])
            self.assertEqual(taken["status"], "TAKEN_OVER")

    # 规则 5：旧记录缺更换关系时待核，补齐前不能确认接管
    def test_pending_review_blocks_takeover_until_supplemented(self):
        with self.assertRaises(HandoverError) as ctx:
            self.svc.confirm_takeover(900)
        self.assertEqual(ctx.exception.code, "ORDER_PENDING_REVIEW")

        with self.assertRaises(HandoverError):
            self.svc.supplement_relation(900, {"new_device_code": "  "})

        supplemented = self.svc.supplement_relation(
            900, {"new_device_code": "EX-NEW-009", "new_device_type": "EXTINGUISHER", "building_id": 1})
        self.assertEqual(supplemented["status"], "PRE_OCCUPIED")
        taken = self.svc.confirm_takeover(900)
        self.assertEqual(taken["status"], "TAKEN_OVER")

    def test_register_legacy_pending_is_idempotent(self):
        first = self.svc.register_pending_legacy(9, "缺更换关系")
        second = self.svc.register_pending_legacy(9, "缺更换关系")
        self.assertEqual(first["id"], second["id"])

    # 冲突草稿化解：改挂另一台旧设备后可以继续
    def test_conflict_draft_can_be_retargeted(self):
        first = self.svc.submit(
            submit_payload(old_device_id=3, client_token="a", new_device_code="N-3", qr_code="QR-0003"))
        second = self.svc.submit(
            submit_payload(old_device_id=3, client_token="b", new_device_code="N-3B", qr_code=""))
        self.assertEqual(second["status"], "CONFLICT")
        self.svc.confirm_takeover(first["id"])

        resolved = self.svc.resolve_conflict(
            second["id"], {"old_device_id": 2, "new_device_code": "SD-02-N"})
        self.assertEqual(resolved["status"], "PRE_OCCUPIED")
        self.assertEqual(self.svc.confirm_takeover(resolved["id"])["status"], "TAKEN_OVER")

    # 操作日志覆盖关键动作
    def test_operation_logs_record_handover_actions(self):
        order = self.svc.submit(submit_payload())
        self.svc.confirm_takeover(order["id"])
        actions = {log["action"] for log in self.svc.list_logs()}
        for expected in [
            "ReplacementOrder.submit",
            "FireDevice.create",
            "InspectionTask.transfer",
            "HazardTicket.transfer",
            "InspectionResult.archive",
            "QrArchive.rebind",
            "ReplacementOrder.takeover",
        ]:
            self.assertIn(expected, actions)


if __name__ == "__main__":
    unittest.main()
