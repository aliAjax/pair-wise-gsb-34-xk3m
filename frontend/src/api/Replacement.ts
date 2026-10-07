import type { ReplacementOrder, ReplacementForm } from "../types/ReplacementOrder";
import type { QrArchive } from "../types/QrArchive";
import type { OperationLog } from "../types/OperationLog";
import { mockData } from "../mocks/seedData";

const base = "/api/replacement";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    // 冲突时服务端把保留下来的草稿一起返回，便于前端标出冲突并继续填写。
    const error = new Error(body.message ?? "request failed") as Error & {
      code?: string;
      status?: number;
      conflictOrder?: ReplacementOrder;
    };
    error.code = body.code;
    error.status = res.status;
    error.conflictOrder = body.conflict_order;
    throw error;
  }
  return body as T;
}

export async function listReplacementOrders(): Promise<ReplacementOrder[]> {
  try {
    return await request<ReplacementOrder[]>(`${base}/orders`);
  } catch {
    return [...(mockData.replacementOrder as unknown as ReplacementOrder[])];
  }
}

export async function submitReplacementOrder(
  form: ReplacementForm
): Promise<ReplacementOrder> {
  // 同一 client_token 重试 => 服务端从 staged_steps 续作，不重复登记新设备。
  return request<ReplacementOrder>(`${base}/orders/submit`, {
    method: "POST",
    body: JSON.stringify(form)
  });
}

export async function confirmTakeover(orderId: number): Promise<ReplacementOrder> {
  return request<ReplacementOrder>(`${base}/orders/${orderId}/takeover`, { method: "POST" });
}

export async function supplementRelation(
  orderId: number,
  payload: { new_device_code: string; qr_code?: string; reason?: string }
): Promise<ReplacementOrder> {
  return request<ReplacementOrder>(`${base}/orders/${orderId}/supplement`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function resolveConflict(
  orderId: number,
  payload: Partial<ReplacementForm>
): Promise<ReplacementOrder> {
  return request<ReplacementOrder>(`${base}/orders/${orderId}/resolve-conflict`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function registerLegacyPending(
  oldDeviceId: number,
  reason: string
): Promise<ReplacementOrder> {
  return request<ReplacementOrder>(`${base}/legacy/pending`, {
    method: "POST",
    body: JSON.stringify({ old_device_id: oldDeviceId, reason })
  });
}

export async function listQrArchives(): Promise<QrArchive[]> {
  try {
    return await request<QrArchive[]>(`${base}/qr-archives`);
  } catch {
    return [...(mockData.qrArchive as unknown as QrArchive[])];
  }
}

export async function listOperationLogs(): Promise<OperationLog[]> {
  try {
    return await request<OperationLog[]>(`${base}/logs`);
  } catch {
    return [...(mockData.operationLog as unknown as OperationLog[])];
  }
}
