def create_device_replacement_dto(**overrides):
    row = {"id":1,"request_id":"REQ-20261006-A01","old_device_id":1,"new_device_id":None,"status":"PREOCCUPIED","reason":"灭火器药剂到期报废更换","operator_id":1,"qr_code":None,"created_at":"2026-10-06T09:00:00Z","confirmed_at":None,"conflict_with":None,"steps_done":[],"pending_record_ids":[]}
    row.update(overrides)
    return row
