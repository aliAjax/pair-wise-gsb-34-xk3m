from src.db import db


class FireDeviceRepository:
    def find_all(self):
        return db["fireDevice"]

    def find_by_id(self, device_id):
        return next((d for d in db["fireDevice"] if d["id"] == device_id), None)

    def find_by_code(self, device_code):
        return next((d for d in db["fireDevice"] if d["device_code"] == device_code), None)

    def next_id(self):
        return max((d["id"] for d in db["fireDevice"]), default=0) + 1

    def add(self, row):
        db["fireDevice"].append(row)
        return row
