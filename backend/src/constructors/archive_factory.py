def build_qr_archive_response(row: dict) -> dict:
    return {
        "id": row["id"],
        "qr_code": row["qr_code"],
        "device_id": row["device_id"],
        "bound_at": row.get("bound_at", ""),
        "binding_history": list(row.get("binding_history", []))
    }


def build_operation_log_response(row: dict) -> dict:
    return {
        "id": row["id"],
        "actor": row.get("actor", "system"),
        "action": row["action"],
        "order_id": row.get("order_id"),
        "target_type": row.get("target_type", ""),
        "target_id": str(row.get("target_id", "")),
        "detail": row.get("detail", ""),
        "created_at": row.get("created_at", "")
    }
