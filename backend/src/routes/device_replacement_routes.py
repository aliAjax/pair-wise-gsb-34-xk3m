from fastapi import APIRouter
from src.controllers.device_replacement_controller import backfill_device_replacement, confirm_device_replacement, list_device_replacement, list_device_replacement_logs, submit_device_replacement

router = APIRouter(prefix="/api/device-replacement", tags=["DeviceReplacement"])
router.get("")(list_device_replacement)
router.post("")(submit_device_replacement)
router.post("/{replacement_id}/confirm")(confirm_device_replacement)
router.post("/{replacement_id}/backfill")(backfill_device_replacement)
router.get("/{replacement_id}/logs")(list_device_replacement_logs)
