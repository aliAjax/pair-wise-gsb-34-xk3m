from src.seed import seed
from src.utils.formatters import utc_now

class OperationLogRepository:
    def find_all(self):
        return seed["auditLog"]
    def find_by_target(self, target_type, target_id):
        return [row for row in seed["auditLog"] if row["target_type"] == target_type and row["target_id"] == str(target_id)]
    def record(self, action, target_type, target_id, detail=""):
        row = {"id": len(seed["auditLog"]) + 1, "actor": "system", "action": action, "target_type": target_type, "target_id": str(target_id), "detail": detail, "created_at": utc_now()}
        seed["auditLog"].append(row)
        return row
