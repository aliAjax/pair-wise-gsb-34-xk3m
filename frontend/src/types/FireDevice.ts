export interface FireDevice {
  id: number;
  building_id: number;
  device_code: string;
  device_type: string;
  floor: string;
  location_desc: string;
  install_date: string;
  // IN_SERVICE 在用 / PRE_OCCUPIED 已被更换单预占 / SCRAPPED 已报废
  status: string;
  next_maintenance_at: string;
}
