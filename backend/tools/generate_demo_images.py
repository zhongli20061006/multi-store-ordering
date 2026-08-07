# -*- coding: utf-8 -*-
"""生成演示素材图（阿里云 DashScope 文生图）并写入 uploads/ + 演示库。
运行：python -m tools.generate_demo_images（需 DASHSCOPE_API_KEY）
兼容接口优先，失败自动回退原生异步任务接口；全部失败则打印失败清单。"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from app.core.database import SessionLocal, init_db
from app.core.uploads import UPLOAD_DIR
from app.models import MenuItem, Store, StoreBanner
from sqlalchemy import select, update


KEY = os.environ.get("DASHSCOPE_API_KEY", "")
COMPAT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/images/generations"
NATIVE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
TASK_URL = "https://dashscope.aliyuncs.com/api/v1/tasks/"
COMPAT_MODELS = ["wanx2.1-t2i-turbo", "qwen-image"]


def _request(url: str, payload: dict | None = None, headers: dict | None = None) -> dict:
    merged = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    if headers:
        merged.update(headers)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=merged, method="POST" if payload else "GET")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _download(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read()


def generate(prompt: str, size: str) -> bytes:
    """返回图片字节；兼容接口两次 + 原生异步一次，均失败抛异常。"""
    for model in COMPAT_MODELS:
        try:
            body = _request(COMPAT_URL, {"model": model, "prompt": prompt, "size": size, "n": 1})
            url = body["data"][0]["url"]
            return _download(url)
        except Exception:
            continue
    task = _request(
        NATIVE_URL,
        {"model": "wanx2.1-t2i-turbo", "input": {"prompt": prompt}, "parameters": {"size": size, "n": 1}},
        {"X-DashScope-Async": "enable"},
    )
    task_id = task["output"]["task_id"]
    for _ in range(40):
        time.sleep(3)
        result = _request(TASK_URL + task_id)
        status = result["output"]["task_status"]
        if status == "SUCCEEDED":
            return _download(result["output"]["results"][0]["url"])
        if status in ("FAILED", "CANCELED"):
            break
    raise RuntimeError("native task failed")


def _save(store_id: int, prefix: str, data: bytes) -> str:
    folder = UPLOAD_DIR / str(store_id)
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{prefix}_{int(time.time() * 1000)}.jpg"
    (folder / filename).write_bytes(data)
    return f"/uploads/{store_id}/{filename}"


PROMPTS = {
    "milk_tea": "一杯珍珠奶茶，透明杯，暖米色背景，商业产品摄影，柔和自然光，食欲感，无文字无Logo无水印",
    "milkshake": "一杯草莓奶昔，奶油顶，暖米色背景，商业产品摄影，柔和自然光，食欲感，无文字无Logo无水印",
    "passion_tea": "一杯满杯百香果冰茶，透明杯加冰块，暖米色背景，商业产品摄影，清新通透，无文字无Logo无水印",
    "coconut_latte": "一杯生椰拿铁，分层咖啡与椰奶，暖米色背景，商业产品摄影，柔和自然光，无文字无Logo无水印",
    "store_cover_1": "温馨茶饮店门口，暖橙色门头，木质招牌，傍晚暖光，摄影风格，无文字无Logo无水印",
    "store_cover_2": "现代茶饮店吧台，暖色灯光，店员制作饮品，干净明亮，摄影风格，无文字无Logo无水印",
    "banner_1": "多杯茶饮排列的宽幅促销画面，暖橙色调，干净留白，商业摄影，无文字无Logo无水印",
    "banner_2": "夏日果茶与冰块的特写宽幅画面，清爽暖色调，商业摄影，无文字无Logo无水印",
}


def main() -> None:
    if not KEY:
        print("DASHSCOPE_API_KEY 未设置")
        sys.exit(1)
    init_db()
    db = SessionLocal()
    failed = []
    try:
        size_square = "1024*1024"
        size_wide = "1280*720"
        for name, prompt in PROMPTS.items():
            try:
                size = size_wide if name.startswith("banner") else size_square
                data = generate(prompt, size)
                if name.startswith("banner"):
                    store_id = 1 if name.endswith("1") else 2
                    url = _save(store_id, "banner", data)
                    exists = db.scalar(
                        select(StoreBanner.id).where(
                            StoreBanner.store_id == store_id, StoreBanner.is_active.is_(True)
                        ).limit(1)
                    )
                    if exists:
                        db.execute(
                            update(StoreBanner)
                            .where(StoreBanner.store_id == store_id, StoreBanner.is_active.is_(True))
                            .values(image_url=url, sort_order=1)
                        )
                    else:
                        db.add(StoreBanner(store_id=store_id, image_url=url, sort_order=1, is_active=True))
                else:
                    store_id = 1
                    url = _save(store_id, "item", data)
                    mapping = {
                        "milk_tea": ["招牌奶茶"],
                        "milkshake": ["每日限量奶昔"],
                        "passion_tea": ["满杯百香果"],
                        "coconut_latte": ["生椰拿铁"],
                        "store_cover_1": None,
                        "store_cover_2": None,
                    }
                    names = mapping[name]
                    if names:
                        db.execute(update(MenuItem).where(MenuItem.name.in_(names)).values(image_url=url))
                    elif name == "store_cover_1":
                        db.execute(update(Store).where(Store.id == 1).values(image_url=url))
                    else:
                        db.execute(update(Store).where(Store.id == 2).values(image_url=url))
                db.commit()
                print(f"OK {name}: {url}")
            except Exception as exc:  # noqa: BLE001
                failed.append(name)
                print(f"FAIL {name}: {exc}")
    finally:
        db.close()
    if failed:
        print("FAILED_ITEMS:", ",".join(failed))
        sys.exit(2)
    print("ALL_DONE")


if __name__ == "__main__":
    main()
