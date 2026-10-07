from datetime import datetime, timezone

def audit_target(kind, id):
    return f"{kind}#{id}"

def utc_now():
    return datetime.now(timezone.utc).isoformat()
