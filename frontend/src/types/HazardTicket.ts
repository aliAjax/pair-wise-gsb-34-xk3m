export interface HazardTicket {
  id: number;
  result_id: number;
  device_id: number;
  severity: string;
  owner_id: number;
  deadline: string;
  // OPEN / RECTIFYING / REVIEWING / CLOSED
  rectify_status: string;
  rectify_note: string;
  closed_at: string;
}
