CREATE TABLE IF NOT EXISTS building (
  id INTEGER PRIMARY KEY,
  name TEXT,
  campus TEXT,
  floor_count TEXT,
  fire_grade TEXT,
  manager_id TEXT,
  address_code TEXT
);

-- 消防设备：status 取值 IN_SERVICE(在用) / PRE_OCCUPIED(已被更换单预占) / SCRAPPED(已报废)
CREATE TABLE IF NOT EXISTS fire_device (
  id INTEGER PRIMARY KEY,
  building_id TEXT,
  device_code TEXT UNIQUE,
  device_type TEXT,
  floor TEXT,
  location_desc TEXT,
  install_date TEXT,
  status TEXT,
  next_maintenance_at TEXT
);

CREATE TABLE IF NOT EXISTS inspection_task (
  id INTEGER PRIMARY KEY,
  building_id TEXT,
  inspector_id TEXT,
  device_id TEXT,
  plan_date TEXT,
  task_type TEXT,
  status TEXT,
  checklist_version TEXT,
  finished_at TEXT
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
  device_id TEXT,
  severity TEXT,
  owner_id TEXT,
  deadline TEXT,
  rectify_status TEXT,
  rectify_note TEXT,
  closed_at TEXT
);

-- 二维码档案：同一时刻 device_id 唯一指向一台设备；切换历史放在 binding_history
CREATE TABLE IF NOT EXISTS qr_archive (
  id INTEGER PRIMARY KEY,
  qr_code TEXT UNIQUE,
  device_id INTEGER,
  bound_at TEXT,
  binding_history TEXT
);

-- 设备报废更换单（可恢复交接账）
-- status: DRAFT / PENDING_REVIEW / PRE_OCCUPIED / TAKEN_OVER / CONFLICT
-- staged_steps: 已完成的写入阶段，写入中断后据此续作，避免重复登记新设备
CREATE TABLE IF NOT EXISTS replacement_order (
  id INTEGER PRIMARY KEY,
  order_no TEXT UNIQUE,
  old_device_id INTEGER,
  new_device_id INTEGER,
  new_device_code TEXT,
  qr_code TEXT,
  status TEXT,
  reason TEXT,
  client_token TEXT,
  staged_steps TEXT,
  conflict_with INTEGER,
  transferred_task_ids TEXT,
  transferred_hazard_ids TEXT,
  created_at TEXT,
  preoccupied_at TEXT,
  taken_over_at TEXT
);

-- 并发门禁：同一旧设备同时只允许一张活跃更换单进入预占/接管
CREATE UNIQUE INDEX IF NOT EXISTS uq_replacement_active_old_device
  ON replacement_order(old_device_id)
  WHERE status IN ('PRE_OCCUPIED', 'TAKEN_OVER');

-- 新设备在预占/接管期间只能被一张更换单占用
CREATE UNIQUE INDEX IF NOT EXISTS uq_replacement_active_new_device
  ON replacement_order(new_device_id)
  WHERE status IN ('PRE_OCCUPIED', 'TAKEN_OVER') AND new_device_id IS NOT NULL;

-- 幂等令牌：同一终端重试不重复建单
CREATE UNIQUE INDEX IF NOT EXISTS uq_replacement_client_token
  ON replacement_order(client_token)
  WHERE client_token IS NOT NULL AND client_token <> '';

-- 操作日志：提交、预占、接管、转移、二维码切换、待核补齐等全部留痕
CREATE TABLE IF NOT EXISTS operation_log (
  id INTEGER PRIMARY KEY,
  actor TEXT,
  action TEXT,
  order_id INTEGER,
  target_type TEXT,
  target_id TEXT,
  detail TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY,
  actor TEXT,
  action TEXT,
  target_type TEXT,
  target_id TEXT,
  created_at TEXT
);
