from pydantic import BaseModel


class QrArchive(BaseModel):
    id: int
    qr_code: str
    device_id: int
    bound_at: str
    binding_history: list[dict]
