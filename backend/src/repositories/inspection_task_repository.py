from src.db import db


class InspectionTaskRepository:
    def find_all(self):
        return db["inspectionTask"]

    def find_open_tasks_by_device(self, device_id):
        # 未开始任务：PLANNED 才允许随更换转移；已领取/进行中的留在旧设备。
        return [t for t in db["inspectionTask"]
                if t.get("device_id") == device_id and t["status"] == "PLANNED"]

    def reassign(self, task_id, new_device_id):
        task = next((t for t in db["inspectionTask"] if t["id"] == task_id), None)
        if task is not None:
            task["device_id"] = new_device_id
        return task
