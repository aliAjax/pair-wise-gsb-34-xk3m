def create_hazard_ticket_dto(**overrides):
    row = {"id":1,"result_id":2,"severity":"HIGH","owner_id":1,"deadline":"2026-10-30T09:00:00Z","rectify_status":"OPEN","rectify_note":"等待新灭火器到位","closed_at":"","device_id":1,"replacement_id":None}
    row.update(overrides)
    return row
