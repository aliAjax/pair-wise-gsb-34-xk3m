def audit_target(kind, id):
    return f"{kind}#{id}"


def format_device_service_status(value):
    return {
        "IN_SERVICE": "在用",
        "PRE_OCCUPIED": "已预占",
        "SCRAPPED": "已报废",
    }.get(value, value)


def format_replacement_status(value):
    return {
        "DRAFT": "草稿",
        "PENDING_REVIEW": "关系待核",
        "PRE_OCCUPIED": "已预占待接管",
        "TAKEN_OVER": "已接管",
        "CONFLICT": "更换冲突",
    }.get(value, value)
