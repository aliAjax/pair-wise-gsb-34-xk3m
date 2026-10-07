from src.db import db


class HazardTicketRepository:
    def find_all(self):
        return db["hazardTicket"]

    def find_open_by_device(self, device_id):
        # 未关闭隐患：closed_at 为空且 rectify_status 不是 CLOSED。
        return [h for h in db["hazardTicket"]
                if h.get("device_id") == device_id
                and not h.get("closed_at")
                and h["rectify_status"] != "CLOSED"]

    def reassign(self, ticket_id, new_device_id):
        ticket = next((h for h in db["hazardTicket"] if h["id"] == ticket_id), None)
        if ticket is not None:
            ticket["device_id"] = new_device_id
        return ticket
