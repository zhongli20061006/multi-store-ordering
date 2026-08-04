class BusinessError(Exception):
    """业务规则错误：status_code + 用户可读消息。"""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)
