from pydantic import BaseModel


class OperationLog(BaseModel):
    id: int
    actor: str
    action: str
    order_id: int | None
    target_type: str
    target_id: str
    detail: str
    created_at: str
