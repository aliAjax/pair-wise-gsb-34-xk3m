import { create } from "zustand";
import type { ReplacementOrder, ReplacementForm } from "../types/ReplacementOrder";
import type { QrArchive } from "../types/QrArchive";
import type { OperationLog } from "../types/OperationLog";
import {
  listReplacementOrders,
  submitReplacementOrder,
  confirmTakeover,
  supplementRelation,
  resolveConflict,
  listQrArchives,
  listOperationLogs
} from "../api/Replacement";

type HandoverState = {
  orders: ReplacementOrder[];
  qrArchives: QrArchive[];
  logs: OperationLog[];
  loading: boolean;
  lastError: { code?: string; message: string; conflictOrder?: ReplacementOrder } | null;
  load: () => Promise<void>;
  loadLogs: () => Promise<void>;
  submit: (form: ReplacementForm) => Promise<ReplacementOrder | null>;
  takeover: (orderId: number) => Promise<ReplacementOrder | null>;
  supplement: (
    orderId: number,
    payload: { new_device_code: string; qr_code?: string; reason?: string }
  ) => Promise<ReplacementOrder | null>;
  resolve: (orderId: number, payload: Partial<ReplacementForm>) => Promise<ReplacementOrder | null>;
  clearError: () => void;
};

export const useReplacementStore = create<HandoverState>((set, get) => ({
  orders: [],
  qrArchives: [],
  logs: [],
  loading: false,
  lastError: null,

  async load() {
    set({ loading: true });
    const [orders, qrArchives] = await Promise.all([
      listReplacementOrders(),
      listQrArchives()
    ]);
    set({ orders, qrArchives, loading: false });
  },

  async loadLogs() {
    set({ logs: await listOperationLogs() });
  },

  async submit(form) {
    set({ lastError: null });
    try {
      const order = await submitReplacementOrder(form);
      await get().load();
      return order;
    } catch (err) {
      const e = err as { code?: string; message: string; conflictOrder?: ReplacementOrder };
      set({ lastError: { code: e.code, message: e.message, conflictOrder: e.conflictOrder } });
      await get().load();
      return null;
    }
  },

  async takeover(orderId) {
    set({ lastError: null });
    try {
      const order = await confirmTakeover(orderId);
      await get().load();
      return order;
    } catch (err) {
      const e = err as { code?: string; message: string };
      set({ lastError: { code: e.code, message: e.message } });
      return null;
    }
  },

  async supplement(orderId, payload) {
    set({ lastError: null });
    try {
      const order = await supplementRelation(orderId, payload);
      await get().load();
      return order;
    } catch (err) {
      const e = err as { code?: string; message: string };
      set({ lastError: { code: e.code, message: e.message } });
      return null;
    }
  },

  async resolve(orderId, payload) {
    set({ lastError: null });
    try {
      const order = await resolveConflict(orderId, payload);
      await get().load();
      return order;
    } catch (err) {
      const e = err as { code?: string; message: string };
      set({ lastError: { code: e.code, message: e.message } });
      return null;
    }
  },

  clearError() {
    set({ lastError: null });
  }
}));
