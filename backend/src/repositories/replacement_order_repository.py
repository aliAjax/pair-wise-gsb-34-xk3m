from src.db import db


class ReplacementOrderRepository:
    def find_all(self):
        return db["replacementOrder"]

    def find_by_id(self, order_id):
        return next((o for o in db["replacementOrder"] if o["id"] == order_id), None)

    def find_by_token(self, client_token):
        if not client_token:
            return None
        return next((o for o in db["replacementOrder"] if o.get("client_token") == client_token), None)

    def find_active_by_old_device(self, old_device_id):
        """旧设备上仍未作废的更换单（冲突/待核/预占/接管均算占用）。"""
        return [o for o in db["replacementOrder"]
                if o["old_device_id"] == old_device_id
                and o["status"] in ("PENDING_REVIEW", "PRE_OCCUPIED", "TAKEN_OVER", "CONFLICT")]

    def find_by_new_device(self, new_device_id):
        return next((o for o in db["replacementOrder"] if o.get("new_device_id") == new_device_id), None)

    def next_id(self):
        return max((o["id"] for o in db["replacementOrder"]), default=0) + 1

    def add(self, row):
        db["replacementOrder"].append(row)
        return row
