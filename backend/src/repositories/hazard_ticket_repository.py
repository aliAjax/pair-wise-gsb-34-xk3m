from src.seed import seed

# 已关闭隐患留档旧设备，其余状态都算未关闭
CLOSED_STATUS = "CLOSED"

class HazardTicketRepository:
    def find_all(self):
        return seed["hazardTicket"]
    def find_open_by_device(self, device_id):
        return [row for row in seed["hazardTicket"] if row.get("device_id") == device_id and row.get("rectify_status") != CLOSED_STATUS]
    def save(self, row):
        for index, existing in enumerate(seed["hazardTicket"]):
            if existing["id"] == row["id"]:
                seed["hazardTicket"][index] = row
                return row
        seed["hazardTicket"].append(row)
        return row
