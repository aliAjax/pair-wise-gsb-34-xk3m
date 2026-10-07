import type { FireDevice } from "../types/FireDevice";

export const createDefaultFireDevice = (overrides: Partial<FireDevice> = {}): FireDevice => ({
  id: 1 as never,
  building_id: 1 as never,
  device_code: "FE-1F-001" as never,
  device_type: "EXTINGUISHER" as never,
  floor: "1F" as never,
  location_desc: "一层东侧走廊" as never,
  install_date: "2024-01-15T09:00:00Z" as never,
  status: "ACTIVE" as never,
  next_maintenance_at: "2026-11-01T09:00:00Z" as never,
  qr_code: null as never,
  ...overrides
});

export const createFireDeviceForm = createDefaultFireDevice;
export const createFireDeviceResponse = createDefaultFireDevice;
