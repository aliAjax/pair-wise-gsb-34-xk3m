from fastapi import APIRouter

from src.controllers import replacement_controller as controller

router = APIRouter(prefix="/api/replacement", tags=["Replacement"])

# 更换单：提交（预占，可恢复）、查询、接管确认、补齐关系、化解冲突
router.get("/orders")(controller.list_replacement_orders)
router.get("/orders/{order_id}")(controller.get_replacement_order)
router.post("/orders/submit")(controller.submit_replacement_order)
router.post("/orders/{order_id}/takeover")(controller.confirm_replacement_takeover)
router.post("/orders/{order_id}/supplement")(controller.supplement_replacement_relation)
router.post("/orders/{order_id}/resolve-conflict")(controller.resolve_replacement_conflict)

# 旧报废设备缺少更换关系时登记待核
router.post("/legacy/pending")(controller.register_legacy_pending)

# 二维码档案与操作日志
router.get("/qr-archives")(controller.list_qr_archives)
router.get("/logs")(controller.list_operation_logs)
