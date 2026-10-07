export interface QrArchive {
  id: number;
  qr_code: string;
  device_id: number;
  bound_at: string;
  binding_history: { device_id: number; bound_at: string }[];
}
