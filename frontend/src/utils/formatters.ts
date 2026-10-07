export const formatDate = (value: string) => new Date(value).toLocaleString("zh-CN");
export const formatStatus = (value: string) => value.replace(/_/g, " ");
export const formatNumber = (value: number) => new Intl.NumberFormat("zh-CN").format(value);
export const formatRisk = (value: string) => ({ LOW: "低", MEDIUM: "中", HIGH: "高", CRITICAL: "严重", EXTREME: "极高" }[value] ?? value);
export const formatHandoverStep = (value: string) => ({ REGISTER_NEW_DEVICE: "登记新设备", LINK_OPEN_RECORDS: "挂接在途记录", TRANSFER_TASKS: "转交未开始任务", TRANSFER_HAZARDS: "转交未关闭隐患", REBIND_QR: "换绑二维码", RETIRE_OLD_DEVICE: "报废旧设备", ACTIVATE_NEW_DEVICE: "启用新设备" }[value] ?? value);
export const formatQrBinding = (value: string | null | undefined) => value ?? "未绑定";
