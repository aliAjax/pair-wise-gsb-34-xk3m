import type { DeviceReplacement } from "../types/DeviceReplacement";

export const createDefaultDeviceReplacement = (overrides: Partial<DeviceReplacement> = {}): DeviceReplacement => ({
  id: 1 as never,
  request_id: "REQ-20261006-A01" as never,
  old_device_id: 1 as never,
  new_device_id: null as never,
  status: "PREOCCUPIED" as never,
  reason: "灭火器药剂到期报废更换" as never,
  operator_id: 1 as never,
  qr_code: null as never,
  created_at: "2026-10-06T09:00:00Z" as never,
  confirmed_at: null as never,
  conflict_with: null as never,
  steps_done: [] as never,
  pending_record_ids: [] as never,
  ...overrides
});

export const createDeviceReplacementForm = createDefaultDeviceReplacement;
export const createDeviceReplacementResponse = createDefaultDeviceReplacement;

// 离线兜底：本地推进交接账状态，与后端交接步骤（constants/handover_step）保持一致
export const applyLocalConfirm = (order: DeviceReplacement): DeviceReplacement =>
  order.status === "PREOCCUPIED"
    ? { ...order, status: "CONFIRMED", confirmed_at: new Date().toISOString(), pending_record_ids: [], steps_done: [...order.steps_done, "TRANSFER_TASKS", "TRANSFER_HAZARDS", "REBIND_QR", "RETIRE_OLD_DEVICE", "ACTIVATE_NEW_DEVICE"] }
    : order;

export const applyLocalBackfill = (order: DeviceReplacement): DeviceReplacement =>
  order.status === "PENDING_REVIEW" ? { ...order, status: "PREOCCUPIED", pending_record_ids: [] } : order;
