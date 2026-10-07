from src.db.memory_store import HANDOVER_STEPS


def create_replacement_order_form(**overrides):
    """前端/调用方提交更换单时的默认表单结构。"""
    row = {
        "old_device_id": 0,
        "new_device_code": "",
        "new_device_type": "EXTINGUISHER",
        "qr_code": "",
        "building_id": 0,
        "floor": "",
        "location_desc": "",
        "install_date": "",
        "next_maintenance_at": "",
        "reason": "",
        "client_token": ""
    }
    row.update(overrides)
    return row


def build_replacement_order_response(order: dict) -> dict:
    """响应 DTO：显式暴露交接账关注的阶段与冲突字段。"""
    return {
        "id": order["id"],
        "order_no": order["order_no"],
        "old_device_id": order["old_device_id"],
        "new_device_id": order.get("new_device_id"),
        "new_device_code": order.get("new_device_code", ""),
        "qr_code": order.get("qr_code", ""),
        "status": order["status"],
        "reason": order.get("reason", ""),
        "client_token": order.get("client_token", ""),
        "staged_steps": list(order.get("staged_steps", [])),
        "remaining_steps": [s for s in HANDOVER_STEPS if s not in order.get("staged_steps", [])],
        "conflict_with": order.get("conflict_with"),
        "transferred_task_ids": list(order.get("transferred_task_ids", [])),
        "transferred_hazard_ids": list(order.get("transferred_hazard_ids", [])),
        "created_at": order.get("created_at", ""),
        "preoccupied_at": order.get("preoccupied_at", ""),
        "taken_over_at": order.get("taken_over_at", "")
    }
