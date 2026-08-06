class BusinessError(Exception):
    """业务规则错误：status_code + 用户可读消息 + 可选结构化 detail。"""

    def __init__(self, status_code: int, message: str, detail=None):
        self.status_code = status_code
        self.message = message
        self.detail = detail
        super().__init__(message)
