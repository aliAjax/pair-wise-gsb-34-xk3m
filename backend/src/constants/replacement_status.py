"""设备报废更换交接相关枚举。"""

# 更换单状态
ReplacementStatus = [
  "DRAFT",            # 草稿（冲突后保留填写内容）
  "PENDING_REVIEW",   # 旧记录缺少更换关系，待核
  "PRE_OCCUPIED",     # 新设备已预占，等待接管确认
  "TAKEN_OVER",       # 已完成接管
  "CONFLICT"          # 与已存在的更换单冲突
]

# 设备在更换流程中的附加状态
DeviceServiceStatus = [
  "IN_SERVICE",       # 在用
  "PRE_OCCUPIED",     # 已被更换单预占，尚未接管
  "SCRAPPED"          # 已报废
]

# 接管交接单的写入阶段：顺序必须固定，写入中断后按此顺序续作
ReplacementStage = [
  "register_new_device",  # 登记新设备
  "preoccupy_new_device", # 预占新设备
  "bind_qr_draft"         # 建立二维码待切换绑定
]
