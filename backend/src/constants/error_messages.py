ERROR_MESSAGES = {
  "AUTH_REQUIRED": "missing token",
  "RBAC_DENIED": "role denied",
  "VALIDATION_FAILED": "invalid payload",
  "DEVICE_NOT_FOUND": "设备不存在: {device_id}",
  "OLD_DEVICE_NOT_SCRAPPABLE": "旧设备当前状态不允许报废更换: {status}",
  "NEW_DEVICE_ALREADY_PREOCCUPIED": "新设备 {device_code} 已被更换单 {order_no} 预占，禁止重复占用",
  "NEW_DEVICE_CODE_DUPLICATED": "新设备编号 {device_code} 已登记，续作时不会重复登记",
  "REPLACEMENT_CONFLICT": "旧设备 {old_device_code} 的更换单 {order_no} 已完成接管，本单保留为冲突草稿",
  "QR_ALREADY_BOUND": "二维码 {qr_code} 当前已绑定设备 {device_id}，同一时刻只能绑定一台设备",
  "ORDER_NOT_FOUND": "更换单不存在: {order_id}",
  "ORDER_PENDING_REVIEW": "更换单 {order_no} 旧记录缺少更换关系，补齐前不能确认接管",
  "ORDER_NOT_PREOCCUPIED": "更换单 {order_no} 尚未完成预占，不能接管",
  "RELATION_INCOMPLETE": "更换关系不完整：{field} 缺失"
}
