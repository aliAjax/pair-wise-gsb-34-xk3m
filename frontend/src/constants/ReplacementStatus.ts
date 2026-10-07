export const ReplacementStatus = ["PREOCCUPIED", "PENDING_REVIEW", "CONFIRMED", "CONFLICT"] as const;
export type ReplacementStatus = (typeof ReplacementStatus)[number];
export const ReplacementStatusText: Record<ReplacementStatus, string> = {
  PREOCCUPIED: "已预占",
  PENDING_REVIEW: "待核",
  CONFIRMED: "已接管",
  CONFLICT: "冲突"
};
