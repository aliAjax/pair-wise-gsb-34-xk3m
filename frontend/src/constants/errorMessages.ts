export const ERROR_MESSAGES = {
  AUTH_REQUIRED: "请先登录后再继续操作",
  RBAC_DENIED: "当前角色没有执行该动作的权限",
  VALIDATION_FAILED: "表单字段缺失或格式错误",
  RATE_LIMITED: "请求过于频繁，请稍后再试",
  DEVICE_NOT_FOUND: "设备不存在",
  OLD_DEVICE_NOT_SCRAPPABLE: "旧设备当前状态不允许报废更换",
  NEW_DEVICE_ALREADY_PREOCCUPIED: "新设备已被另一张更换单预占，禁止重复占用",
  NEW_DEVICE_CODE_DUPLICATED: "新设备已登记，续作不会重复登记",
  REPLACEMENT_CONFLICT: "旧设备的更换单已完成接管，本单已保留为冲突草稿",
  QR_ALREADY_BOUND: "二维码当前绑定在其他设备上，同一时刻只能绑定一台设备",
  ORDER_NOT_FOUND: "更换单不存在",
  ORDER_PENDING_REVIEW: "旧记录缺少更换关系，补齐前不能确认接管",
  ORDER_NOT_PREOCCUPIED: "更换单尚未完成预占，不能接管",
  RELATION_INCOMPLETE: "更换关系不完整，请补齐新设备等字段"
} as const;
