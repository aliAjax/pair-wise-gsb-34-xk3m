from src.db import db


class InspectionResultRepository:
    def find_all(self):
        return db["inspectionResult"]

    def find_by_device(self, device_id):
        # 旧巡检结果永远留在旧设备档案，接管不移动这些行。
        return [r for r in db["inspectionResult"] if r.get("device_id") == device_id]
