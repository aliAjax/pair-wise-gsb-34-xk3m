export const ERROR_MESSAGES = {
  AUTH_REQUIRED: "请先登录后再继续操作",
  RBAC_DENIED: "当前角色没有执行该动作的权限",
  VALIDATION_FAILED: "表单字段缺失或格式错误",
  RATE_LIMITED: "请求过于频繁，请稍后再试",
  DEVICE_NOT_FOUND: "旧设备不存在或已注销",
  REPLACEMENT_NOT_FOUND: "更换单不存在",
  REPLACEMENT_CONFLICT: "旧设备已被另一张更换单接管，本单保留填写并标记冲突",
  REPLACEMENT_PENDING_REVIEW: "存在缺少更换关系的旧记录，补齐前不能确认接管",
  REPLACEMENT_INVALID_STATE: "当前更换单状态不允许该操作"
};
