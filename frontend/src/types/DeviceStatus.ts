export const DeviceStatus = ["ACTIVE", "PREOCCUPIED", "RETIRED", "RELEASED"] as const;
export type DeviceStatus = (typeof DeviceStatus)[number];
export const DeviceStatusText: Record<DeviceStatus, string> = {
  ACTIVE: "在用",
  PREOCCUPIED: "预占中",
  RETIRED: "已报废",
  RELEASED: "预占释放"
};
