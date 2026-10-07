import { create } from "zustand";
import { backfillDeviceReplacement, confirmDeviceReplacement, listDeviceReplacement, submitDeviceReplacement } from "../api/DeviceReplacement";
import { applyLocalBackfill, applyLocalConfirm } from "../constructors/DeviceReplacementConstructor";
import type { DeviceReplacement, DeviceReplacementPayload } from "../types/DeviceReplacement";

type State = {
  rows: DeviceReplacement[];
  loading: boolean;
  error: string | null;
  load: () => Promise<void>;
  submit: (payload: DeviceReplacementPayload) => Promise<void>;
  confirm: (id: number) => Promise<void>;
  backfill: (id: number) => Promise<void>;
};

export const useDeviceReplacementStore = create<State>((set, get) => ({
  rows: [],
  loading: false,
  error: null,
  async load() {
    set({ loading: true });
    set({ rows: await listDeviceReplacement(), loading: false });
  },
  async submit(payload) {
    set({ error: null });
    try {
      const saved = await submitDeviceReplacement(payload);
      set((state) => {
        // 同一 request_id 重复提交 → 续作已预占单，不重复登记
        const exists = state.rows.some((row) => row.request_id === saved.request_id);
        return { rows: exists ? state.rows.map((row) => (row.request_id === saved.request_id ? saved : row)) : [...state.rows, saved] };
      });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : String(error) });
    }
  },
  async confirm(id) {
    set({ error: null });
    try {
      const updated = await confirmDeviceReplacement(id);
      set((state) => ({ rows: state.rows.map((row) => (row.id === id ? updated ?? applyLocalConfirm(row) : row)) }));
    } catch (error) {
      // 冲突/待核：后端已改写交接账状态，重新拉取
      set({ error: error instanceof Error ? error.message : String(error) });
      await get().load();
    }
  },
  async backfill(id) {
    set({ error: null });
    try {
      const updated = await backfillDeviceReplacement(id);
      set((state) => ({ rows: state.rows.map((row) => (row.id === id ? updated ?? applyLocalBackfill(row) : row)) }));
    } catch (error) {
      set({ error: error instanceof Error ? error.message : String(error) });
      await get().load();
    }
  }
}));
