import type { FireDevice } from "../types/FireDevice";

export const createDefaultFireDevice = (overrides: Partial<FireDevice> = {}): FireDevice => ({
  id: 1 as never,
  building_id: 1 as never,
  device_code: "HQ-01-001" as never,
  device_type: "HYDRANT" as never,
  floor: "1F" as never,
  location_desc: "location desc 1" as never,
  install_date: "2022-06-11T09:00:00Z" as never,
  status: "IN_SERVICE" as never,
  next_maintenance_at: "2026-06-11T09:00:00Z" as never,
  ...overrides
});

export const createFireDeviceForm = createDefaultFireDevice;
export const createFireDeviceResponse = createDefaultFireDevice;
