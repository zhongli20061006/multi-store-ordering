"""CSV 导出公共工具：公式注入转义 + UTC+8 时间格式化。"""
from app.services.order_service import CN_TZ


def csv_safe(value) -> str:
    """CSV 公式注入防护：以 = + - @ 或 Tab/CR 开头的单元格前置单引号。"""
    if value is None:
        return ""
    text = str(value)
    if text[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + text
    return text


def format_local(dt) -> str:
    """落库时间为无时区 UTC，转 UTC+8 后格式化。"""
    offset = CN_TZ.utcoffset(None)
    return (dt + offset).strftime("%Y-%m-%d %H:%M:%S")
