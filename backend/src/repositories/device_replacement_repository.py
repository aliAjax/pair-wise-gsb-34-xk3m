from src.seed import seed

OPEN_STATUSES = ("PREOCCUPIED", "PENDING_REVIEW")

class DeviceReplacementRepository:
    def find_all(self):
        return seed["deviceReplacement"]
    def find_by_id(self, replacement_id):
        if replacement_id is None:
            return None
        for row in seed["deviceReplacement"]:
            if row["id"] == replacement_id:
                return row
        return None
    def find_by_request_id(self, request_id):
        for row in seed["deviceReplacement"]:
            if row["request_id"] == request_id:
                return row
        return None
    def find_confirmed_for_device(self, old_device_id, exclude_id=None):
        for row in seed["deviceReplacement"]:
            if row["old_device_id"] == old_device_id and row["status"] == "CONFIRMED" and row["id"] != exclude_id:
                return row
        return None
    def find_open_for_device(self, old_device_id, exclude_id=None):
        return [row for row in seed["deviceReplacement"] if row["old_device_id"] == old_device_id and row["status"] in OPEN_STATUSES and row["id"] != exclude_id]
    def next_id(self):
        return max([row["id"] for row in seed["deviceReplacement"]] + [0]) + 1
    def save(self, row):
        for index, existing in enumerate(seed["deviceReplacement"]):
            if existing["id"] == row["id"]:
                seed["deviceReplacement"][index] = row
                return row
        seed["deviceReplacement"].append(row)
        return row
