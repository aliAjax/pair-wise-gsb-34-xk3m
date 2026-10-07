CREATE TABLE IF NOT EXISTS building (
  id INTEGER PRIMARY KEY,
  name TEXT,
  campus TEXT,
  floor_count TEXT,
  fire_grade TEXT,
  manager_id TEXT,
  address_code TEXT
);

CREATE TABLE IF NOT EXISTS fire_device (
  id INTEGER PRIMARY KEY,
  building_id TEXT,
  device_code TEXT,
  device_type TEXT,
  floor TEXT,
  location_desc TEXT,
  install_date TEXT,
  status TEXT,
  next_maintenance_at TEXT,
  qr_code TEXT
);

-- 二维码同一时刻只绑定一台设备
CREATE UNIQUE INDEX IF NOT EXISTS fire_device_qr_code_unique ON fire_device (qr_code) WHERE qr_code IS NOT NULL;

CREATE TABLE IF NOT EXISTS inspection_task (
  id INTEGER PRIMARY KEY,
  building_id TEXT,
  inspector_id TEXT,
  plan_date TEXT,
  task_type TEXT,
  status TEXT,
  checklist_version TEXT,
  finished_at TEXT,
  device_id TEXT,
  replacement_id TEXT
);

CREATE TABLE IF NOT EXISTS inspection_result (
  id INTEGER PRIMARY KEY,
  task_id TEXT,
  device_id TEXT,
  item_code TEXT,
  result_status TEXT,
  measured_value TEXT,
  photo_url TEXT,
  note TEXT
);

CREATE TABLE IF NOT EXISTS hazard_ticket (
  id INTEGER PRIMARY KEY,
  result_id TEXT,
  severity TEXT,
  owner_id TEXT,
  deadline TEXT,
  rectify_status TEXT,
  rectify_note TEXT,
  closed_at TEXT,
  device_id TEXT,
  replacement_id TEXT
);

-- 报废更换交接账：预占 → 待核 → 接管 / 冲突，全程按 steps_done 落账可恢复
CREATE TABLE IF NOT EXISTS device_replacement (
  id INTEGER PRIMARY KEY,
  request_id TEXT UNIQUE,
  old_device_id TEXT,
  new_device_id TEXT,
  status TEXT,
  reason TEXT,
  operator_id TEXT,
  qr_code TEXT,
  created_at TEXT,
  confirmed_at TEXT,
  conflict_with TEXT,
  steps_done TEXT,
  pending_record_ids TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY,
  actor TEXT,
  action TEXT,
  target_type TEXT,
  target_id TEXT,
  detail TEXT,
  created_at TEXT
);
