"""可恢复交接账的进程内状态库。

设计目标：
- 所有表集中在单一可变状态对象，服务层通过 get_lock() 串行化写入，保证
  两台终端并发提交时只有一份更换单能接管旧设备。
- 每张更换单维护 staged_steps / failure_stage：写入中断后重试只从已完成
  阶段之后续作，不会重复登记新设备。
"""
import threading
import copy

from src.seed import seed as _seed

# 设备状态：IN_SERVICE 在用 / PRE_OCCUPIED 已被更换单预占 / SCRAPPED 已报废 / IN_SERVICE_NEW 接管后启用
DEVICE_IN_SERVICE = "IN_SERVICE"
DEVICE_PRE_OCCUPIED = "PRE_OCCUPIED"
DEVICE_SCRAPPED = "SCRAPPED"

# 更换单状态：DRAFT 冲突保留待处理 / PENDING_REVIEW 旧记录缺更换关系待核 /
# PRE_OCCUPIED 已预占待接管 / TAKEN_OVER 已接管 / CONFLICT 与另一单冲突
ORDER_DRAFT = "DRAFT"
ORDER_PENDING_REVIEW = "PENDING_REVIEW"
ORDER_PRE_OCCUPIED = "PRE_OCCUPIED"
ORDER_TAKEN_OVER = "TAKEN_OVER"
ORDER_CONFLICT = "CONFLICT"

# 更换单写入阶段（顺序即续作检查顺序）
STEP_REGISTER_DEVICE = "register_new_device"
STEP_PREOCCUPY = "preoccupy_new_device"
STEP_BIND_QR_DRAFT = "bind_qr_draft"

HANDOVER_STEPS = [STEP_REGISTER_DEVICE, STEP_PREOCCUPY, STEP_BIND_QR_DRAFT]


def _build_state():
    state = {
        "building": copy.deepcopy(_seed["building"]),
        "fireDevice": copy.deepcopy(_seed["fireDevice"]),
        "inspectionTask": copy.deepcopy(_seed["inspectionTask"]),
        "inspectionResult": copy.deepcopy(_seed["inspectionResult"]),
        "hazardTicket": copy.deepcopy(_seed["hazardTicket"]),
        "qrArchive": copy.deepcopy(_seed["qrArchive"]),
        "replacementOrder": copy.deepcopy(_seed["replacementOrder"]),
        "operationLog": copy.deepcopy(_seed["operationLog"]),
    }
    # 种子里的设备默认为在用状态。
    for device in state["fireDevice"]:
        device.setdefault("status", DEVICE_IN_SERVICE)
        if device["status"] in ("PLANNED", "SUBMITTED", "IN_PROGRESS"):
            device["status"] = DEVICE_IN_SERVICE
    return state


db = _build_state()

# 串行锁：提交、接管、冲突化解等写操作全程持锁。
_lock = threading.RLock()


def get_lock():
    return _lock


def reset_db(fail_after_stage=None):
    """测试辅助：原地恢复种子状态（保持 db 对象引用不变），并可注入故障点。"""
    fresh = _build_state()
    fresh["_fail_after_stage"] = fail_after_stage
    with _lock:
        db.clear()
        db.update(fresh)
