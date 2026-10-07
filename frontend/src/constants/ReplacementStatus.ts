// 设备报废更换交接枚举（与后端 src/constants/replacement_status.py 同步）
export const REPLACEMENT_STATUS = {
  DRAFT: "DRAFT",
  PENDING_REVIEW: "PENDING_REVIEW",
  PRE_OCCUPIED: "PRE_OCCUPIED",
  TAKEN_OVER: "TAKEN_OVER",
  CONFLICT: "CONFLICT"
} as const;

export const ReplacementStatusText: Record<string, string> = {
  DRAFT: "草稿",
  PENDING_REVIEW: "关系待核",
  PRE_OCCUPIED: "已预占待接管",
  TAKEN_OVER: "已接管",
  CONFLICT: "更换冲突"
};

// 预占写入阶段：顺序固定，写入中断后从下一阶段续作
export const REPLACEMENT_STAGES = [
  { stage: "register_new_device", text: "登记新设备" },
  { stage: "preoccupy_new_device", text: "预占新设备" },
  { stage: "bind_qr_draft", text: "二维码待切换" }
] as const;

export const DEVICE_SERVICE_STATUS_TEXT: Record<string, string> = {
  IN_SERVICE: "在用",
  PRE_OCCUPIED: "已预占",
  SCRAPPED: "已报废"
};
