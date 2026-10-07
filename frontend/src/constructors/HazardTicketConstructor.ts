import type { HazardTicket } from "../types/HazardTicket";

export const createDefaultHazardTicket = (overrides: Partial<HazardTicket> = {}): HazardTicket => ({
  id: 1 as never,
  result_id: 2 as never,
  severity: "HIGH" as never,
  owner_id: 1 as never,
  deadline: "2026-10-30T09:00:00Z" as never,
  rectify_status: "OPEN" as never,
  rectify_note: "等待新灭火器到位" as never,
  closed_at: "" as never,
  device_id: 1 as never,
  replacement_id: null as never,
  ...overrides
});

export const createHazardTicketForm = createDefaultHazardTicket;
export const createHazardTicketResponse = createDefaultHazardTicket;
