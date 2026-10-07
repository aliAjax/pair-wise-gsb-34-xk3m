from fastapi import Request

from src.services.replacement_service import ReplacementService
from src.utils.errors import HandoverError
from src.constructors.replacement_order_factory import build_replacement_order_response
from src.constructors.archive_factory import build_qr_archive_response, build_operation_log_response

service = ReplacementService()


def _actor(request: Request) -> str:
    user = getattr(getattr(request, "state", None), "user", None) or {}
    return str(user.get("id") or user.get("role") or "inspector")


def list_replacement_orders():
    return service.list_orders()


def get_replacement_order(order_id: int):
    return service.get_order(order_id)


async def submit_replacement_order(request: Request):
    payload = await request.json()
    try:
        order = service.submit(payload, actor=_actor(request))
        return order
    except HandoverError as exc:
        # 控制器二次包装：冲突也返回可继续编辑的草稿内容。
        draft = service.orders.find_by_token(payload.get("client_token", "")) if payload else None
        return _error(exc, draft)


async def confirm_replacement_takeover(order_id: int, request: Request):
    try:
        return service.confirm_takeover(order_id, actor=_actor(request))
    except HandoverError as exc:
        return _error(exc)


async def supplement_replacement_relation(order_id: int, request: Request):
    payload = await request.json()
    try:
        return service.supplement_relation(order_id, payload, actor=_actor(request))
    except HandoverError as exc:
        return _error(exc)


async def register_legacy_pending(request: Request):
    payload = await request.json()
    old_device_id = payload.get("old_device_id")
    reason = payload.get("reason", "")
    try:
        return service.register_pending_legacy(old_device_id, reason, actor=_actor(request))
    except HandoverError as exc:
        return _error(exc)


async def resolve_replacement_conflict(order_id: int, request: Request):
    payload = await request.json()
    try:
        return service.resolve_conflict(order_id, payload, actor=_actor(request))
    except HandoverError as exc:
        return _error(exc)


def list_qr_archives():
    return [build_qr_archive_response(q) for q in service.qrs.find_all()]


def list_operation_logs():
    return [build_operation_log_response(l) for l in service.list_logs()]


def _error(exc: HandoverError, draft=None):
    from fastapi.responses import JSONResponse
    body = {
        "code": exc.code,
        "message": exc.message,
    }
    if draft is not None:
        body["conflict_order"] = build_replacement_order_response(draft)
    return JSONResponse(status_code=exc.status_code, content=body)
