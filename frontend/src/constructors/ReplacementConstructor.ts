import type { ReplacementForm } from "../types/ReplacementOrder";

// 更换单默认表单：冲突时填写内容会按此结构原样保留
export function createReplacementForm(overrides: Partial<ReplacementForm> = {}): ReplacementForm {
  return {
    old_device_id: 0,
    new_device_code: "",
    new_device_type: "EXTINGUISHER",
    qr_code: "",
    building_id: 0,
    floor: "",
    location_desc: "",
    reason: "",
    // 幂等令牌：同一终端重试时复用，服务端据此从已预占阶段续作
    client_token: `cli-${Date.now()}-${Math.floor(Math.random() * 1e6)}`,
    ...overrides
  };
}

export function createReplacementStatusPayload(order: {
  status: string;
  staged_steps: string[];
  remaining_steps: string[];
}) {
  return {
    label: order.status,
    progress: order.staged_steps.length,
    total: order.staged_steps.length + order.remaining_steps.length
  };
}
