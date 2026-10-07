def create_inspection_task_dto(**overrides):
    row = {"id":1,"building_id":1,"inspector_id":1,"plan_date":"2026-10-15T09:00:00Z","task_type":"EXTINGUISHER","status":"PLANNED","checklist_version":"v2026.09","finished_at":"","device_id":1,"replacement_id":None}
    row.update(overrides)
    return row
