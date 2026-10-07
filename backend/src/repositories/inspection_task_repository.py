from src.seed import seed

# 未开始任务：只有 PLANNED 状态才随更换单转交新设备
UNSTARTED_STATUS = "PLANNED"

class InspectionTaskRepository:
    def find_all(self):
        return seed["inspectionTask"]
    def find_open_by_device(self, device_id):
        return [row for row in seed["inspectionTask"] if row.get("device_id") == device_id and row.get("status") == UNSTARTED_STATUS]
    def save(self, row):
        for index, existing in enumerate(seed["inspectionTask"]):
            if existing["id"] == row["id"]:
                seed["inspectionTask"][index] = row
                return row
        seed["inspectionTask"].append(row)
        return row
