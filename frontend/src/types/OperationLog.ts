export interface OperationLog {
  id: number;
  actor: string;
  action: string;
  order_id: number | null;
  target_type: string;
  target_id: string;
  detail: string;
  created_at: string;
}
