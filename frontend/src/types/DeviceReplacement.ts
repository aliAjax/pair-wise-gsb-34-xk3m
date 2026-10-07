export interface DeviceReplacement {
  id: number;
  request_id: string;
  old_device_id: number;
  new_device_id: number | null;
  status: string;
  reason: string;
  operator_id: number;
  qr_code: string | null;
  created_at: string;
  confirmed_at: string | null;
  conflict_with: number | null;
  steps_done: string[];
  pending_record_ids: string[];
}

export interface DeviceReplacementPayload {
  request_id: string;
  old_device_id: number;
  reason: string;
  new_device_code?: string;
  operator_id?: number;
}
