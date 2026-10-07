from src.db import db


class QrArchiveRepository:
    def find_all(self):
        return db["qrArchive"]

    def find_by_code(self, qr_code):
        return next((q for q in db["qrArchive"] if q["qr_code"] == qr_code), None)

    def find_by_device(self, device_id):
        return next((q for q in db["qrArchive"] if q["device_id"] == device_id), None)

    def next_id(self):
        return max((q["id"] for q in db["qrArchive"]), default=0) + 1

    def rebind(self, qr_code, new_device_id, bound_at):
        archive = self.find_by_code(qr_code)
        archive["device_id"] = new_device_id
        archive["bound_at"] = bound_at
        archive.setdefault("binding_history", []).append(
            {"device_id": new_device_id, "bound_at": bound_at}
        )
        return archive

    def bind_new(self, qr_code, device_id, bound_at):
        row = {
            "id": self.next_id(),
            "qr_code": qr_code,
            "device_id": device_id,
            "bound_at": bound_at,
            "binding_history": [{"device_id": device_id, "bound_at": bound_at}],
        }
        db["qrArchive"].append(row)
        return row
