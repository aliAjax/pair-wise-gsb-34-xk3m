from src.seed import seed
class FireDeviceRepository:
    def find_all(self):
        return seed["fireDevice"]
    def find_by_id(self, device_id):
        if device_id is None:
            return None
        for row in seed["fireDevice"]:
            if row["id"] == device_id:
                return row
        return None
    def next_id(self):
        return max([row["id"] for row in seed["fireDevice"]] + [0]) + 1
    def save(self, row):
        for index, existing in enumerate(seed["fireDevice"]):
            if existing["id"] == row["id"]:
                seed["fireDevice"][index] = row
                return row
        seed["fireDevice"].append(row)
        return row
