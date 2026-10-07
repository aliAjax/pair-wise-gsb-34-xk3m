from fastapi import HTTPException

from src.services.device_replacement_service import DeviceReplacementService, ReplacementError
from src.types.device_replacement_payload import DeviceReplacementPayload
from src.utils.formatters import to_error_payload

service = DeviceReplacementService()

STATUS_BY_CODE = {"REPLACEMENT_CONFLICT": 409, "REPLACEMENT_PENDING_REVIEW": 409, "REPLACEMENT_INVALID_STATE": 409, "REPLACEMENT_NOT_FOUND": 404, "DEVICE_NOT_FOUND": 404}


def _raise(exc):
    raise HTTPException(status_code=STATUS_BY_CODE.get(exc.code, 400), detail=to_error_payload(exc))


def list_device_replacement():
    return service.list()


def submit_device_replacement(payload: DeviceReplacementPayload):
    try:
        return service.submit(payload)
    except ReplacementError as exc:
        _raise(exc)


def confirm_device_replacement(replacement_id: int):
    try:
        return service.confirm(replacement_id)
    except ReplacementError as exc:
        _raise(exc)


def backfill_device_replacement(replacement_id: int):
    try:
        return service.backfill(replacement_id)
    except ReplacementError as exc:
        _raise(exc)


def list_device_replacement_logs(replacement_id: int):
    try:
        return service.logs_of(replacement_id)
    except ReplacementError as exc:
        _raise(exc)
