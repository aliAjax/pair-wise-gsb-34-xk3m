from pydantic import BaseModel


class ReplacementOrder(BaseModel):
    id: int
    order_no: str
    old_device_id: int
    new_device_id: int | None
    new_device_code: str
    qr_code: str
    status: str
    reason: str
    client_token: str
    staged_steps: list[str]
    conflict_with: int | None
    transferred_task_ids: list[int]
    transferred_hazard_ids: list[int]
    created_at: str
    preoccupied_at: str
    taken_over_at: str
