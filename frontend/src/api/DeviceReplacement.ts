import { mockData } from "../mocks/seedData";
import { createDeviceReplacementResponse } from "../constructors/DeviceReplacementConstructor";
import type { DeviceReplacement, DeviceReplacementPayload } from "../types/DeviceReplacement";

const endpoint = "/api/device-replacement";

async function parseError(res: Response): Promise<Error> {
  try {
    const data = await res.json();
    return new Error(data?.detail?.message ?? `请求失败（${res.status}）`);
  } catch {
    return new Error(`请求失败（${res.status}）`);
  }
}

export async function listDeviceReplacement(): Promise<DeviceReplacement[]> {
  if (typeof fetch !== "undefined" && endpoint.startsWith("/api") && true) {
    try {
      const res = await fetch(endpoint);
      if (res.ok) return await res.json();
    } catch {
      // Local mock fallback keeps the UI available during offline review.
    }
  }
  return [...(mockData.deviceReplacement as unknown as DeviceReplacement[])];
}

export async function submitDeviceReplacement(payload: DeviceReplacementPayload): Promise<DeviceReplacement> {
  try {
    const res = await fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    if (!res.ok) throw await parseError(res);
    return await res.json();
  } catch (error) {
    if (error instanceof TypeError) {
      // 离线兜底：本地构造已预占单（同一 request_id 续作语义由 store 保证）
      return createDeviceReplacementResponse({ ...payload, id: Date.now() % 100000, new_device_id: null, status: "PREOCCUPIED", created_at: new Date().toISOString(), steps_done: ["REGISTER_NEW_DEVICE", "LINK_OPEN_RECORDS"] });
    }
    throw error;
  }
}

export async function confirmDeviceReplacement(id: number): Promise<DeviceReplacement | null> {
  try {
    const res = await fetch(`${endpoint}/${id}/confirm`, { method: "POST" });
    if (!res.ok) throw await parseError(res);
    return await res.json();
  } catch (error) {
    if (error instanceof TypeError) return null; // 离线：由 store 本地推进交接账
    throw error;
  }
}

export async function backfillDeviceReplacement(id: number): Promise<DeviceReplacement | null> {
  try {
    const res = await fetch(`${endpoint}/${id}/backfill`, { method: "POST" });
    if (!res.ok) throw await parseError(res);
    return await res.json();
  } catch (error) {
    if (error instanceof TypeError) return null; // 离线：由 store 本地推进交接账
    throw error;
  }
}
