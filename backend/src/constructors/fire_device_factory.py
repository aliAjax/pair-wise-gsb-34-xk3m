def create_fire_device_dto(**overrides):
    row = {"id":1,"building_id":1,"device_code":"FE-1F-001","device_type":"EXTINGUISHER","floor":"1F","location_desc":"一层东侧走廊","install_date":"2024-01-15T09:00:00Z","status":"ACTIVE","next_maintenance_at":"2026-11-01T09:00:00Z","qr_code":None}
    row.update(overrides)
    return row
