// 更换单状态：与 backend/src/constants/replacement_status.py 对应
export type ReplacementStatus =
  | "DRAFT"
  | "PENDING_REVIEW"
  | "PRE_OCCUPIED"
  | "TAKEN_OVER"
  | "CONFLICT";

export interface ReplacementStage {
  stage: string;
  done: boolean;
}

export interface ReplacementOrder {
  id: number;
  order_no: string;
  old_device_id: number;
  new_device_id: number | null;
  new_device_code: string;
  qr_code: string;
  status: ReplacementStatus;
  reason: string;
  client_token: string;
  staged_steps: string[];
  remaining_steps: string[];
  conflict_with: number | null;
  transferred_task_ids: number[];
  transferred_hazard_ids: number[];
  created_at: string;
  preoccupied_at: string;
  taken_over_at: string;
}

export interface ReplacementForm {
  old_device_id: number;
  new_device_code: string;
  new_device_type: string;
  qr_code: string;
  building_id: number;
  floor: string;
  location_desc: string;
  reason: string;
  client_token: string;
}
