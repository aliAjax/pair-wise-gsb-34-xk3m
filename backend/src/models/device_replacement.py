from pydantic import BaseModel
class DeviceReplacement(BaseModel):
    id: int | float
    request_id: str
    old_device_id: int | float
    new_device_id: int | float | None = None
    status: str
    reason: str
    operator_id: int | float
    qr_code: str | None = None
    created_at: str
    confirmed_at: str | None = None
    conflict_with: int | float | None = None
    steps_done: list = []
    pending_record_ids: list = []
