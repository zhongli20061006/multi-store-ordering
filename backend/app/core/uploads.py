# -*- coding: utf-8 -*-
"""商品图片存储：本地 uploads/ 目录；生产切换 OSS 时仅需替换本模块实现（URL 相对路径不变）。"""
import time
from pathlib import Path

from app.core.config import settings
from app.core.errors import BusinessError

UPLOAD_DIR = Path(settings.upload_dir)

ALLOWED_TYPES = {
    "image/jpeg": (".jpg", b"\xff\xd8\xff"),
    "image/png": (".png", b"\x89PNG"),
    "image/webp": (".webp", b"RIFF"),
}
MAX_SIZE = 2 * 1024 * 1024


def save_item_image(data: bytes, store_id: int, item_id: int, content_type: str) -> str:
    spec = ALLOWED_TYPES.get(content_type)
    if spec is None:
        raise BusinessError(400, "仅支持 jpg/png/webp 图片")
    ext, magic = spec
    if not data.startswith(magic):
        raise BusinessError(400, "图片内容与文件类型不符")
    if len(data) > MAX_SIZE:
        raise BusinessError(400, "图片不能超过 2MB")
    folder = UPLOAD_DIR / str(store_id)
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"item_{item_id}_{int(time.time() * 1000)}{ext}"
    (folder / filename).write_bytes(data)
    return f"/uploads/{store_id}/{filename}"


def delete_item_image(relative_path: str | None) -> None:
    if not relative_path or not relative_path.startswith("/uploads/"):
        return
    try:
        (UPLOAD_DIR / relative_path.removeprefix("/uploads/")).unlink(missing_ok=True)
    except OSError:
        pass
