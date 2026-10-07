class HandoverError(Exception):
    """服务层业务异常，携带错误码供控制器二次包装。"""

    def __init__(self, code: str, message: str = "", status_code: int = 400):
        super().__init__(message or code)
        self.code = code
        self.message = message or code
        self.status_code = status_code


class HandoverConflictError(HandoverError):
    """并发更换同一旧设备：首单完成接管，本单保留为冲突草稿。"""

    def __init__(self, code: str, message: str = "", conflict_order_id=None):
        super().__init__(code, message, status_code=409)
        self.conflict_order_id = conflict_order_id
