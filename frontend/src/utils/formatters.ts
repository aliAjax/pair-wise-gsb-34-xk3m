export const formatDate = (value: string) => new Date(value).toLocaleString("zh-CN");
export const formatStatus = (value: string) => value.replace(/_/g, " ");
export const formatNumber = (value: number) => new Intl.NumberFormat("zh-CN").format(value);
export const formatRisk = (value: string) => ({ LOW: "低", MEDIUM: "中", HIGH: "高", CRITICAL: "严重", EXTREME: "极高" }[value] ?? value);

// 设备更换交接状态文案：页面、日志时间线、筛选器共用
export const formatDeviceServiceStatus = (value: string) =>
  ({ IN_SERVICE: "在用", PRE_OCCUPIED: "已预占", SCRAPPED: "已报废" }[value] ?? value);

export const formatReplacementStatus = (value: string) =>
  ({
    DRAFT: "草稿",
    PENDING_REVIEW: "关系待核",
    PRE_OCCUPIED: "已预占待接管",
    TAKEN_OVER: "已接管",
    CONFLICT: "更换冲突"
  }[value] ?? value);
