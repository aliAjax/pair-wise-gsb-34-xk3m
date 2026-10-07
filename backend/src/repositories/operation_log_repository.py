from src.db import db


class OperationLogRepository:
    def find_all(self):
        return db["operationLog"]

    def next_id(self):
        return max((l["id"] for l in db["operationLog"]), default=0) + 1

    def append(self, actor, action, target_type, target_id, detail, order_id=None, created_at=""):
        row = {
            "id": self.next_id(),
            "actor": actor,
            "action": action,
            "order_id": order_id,
            "target_type": target_type,
            "target_id": str(target_id),
            "detail": detail,
            "created_at": created_at
        }
        db["operationLog"].append(row)
        return row
