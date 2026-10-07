from src.utils.errors import HandoverError
from fastapi.responses import JSONResponse


def to_error_payload(exc):
    if isinstance(exc, HandoverError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message},
        )
    return {"code": getattr(exc, "code", "INTERNAL_ERROR"), "message": str(exc)}
