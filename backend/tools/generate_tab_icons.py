# -*- coding: utf-8 -*-
"""生成小程序 tabBar 线性图标（81x81 PNG，透明底）。
运行：python -m tools.generate_tab_icons（需 Pillow）
输出：miniprogram/assets/tabbar/{home,orders,profile}{,-active}.png
常态 #7A736B，选中 #F0643A。"""
from pathlib import Path

from PIL import Image, ImageDraw


OUT_DIR = Path(__file__).resolve().parents[2] / "miniprogram" / "assets" / "tabbar"
NORMAL = (122, 115, 107, 255)  # #7A736B
ACTIVE = (240, 100, 58, 255)  # #F0643A
SIZE = 81
STROKE = 5
SCALE = 3


def _canvas() -> Image.Image:
    return Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))


def _finish(img: Image.Image) -> Image.Image:
    return img.resize((SIZE, SIZE), Image.LANCZOS)


def draw_home(color) -> Image.Image:
    img = _canvas()
    d = ImageDraw.Draw(img)
    s = SCALE
    d.line([(14 * s, 38 * s), (40 * s, 17 * s), (66 * s, 38 * s)], fill=color, width=STROKE * s, joint="curve")
    d.rounded_rectangle([(19 * s, 35 * s), (61 * s, 65 * s)], radius=6 * s, outline=color, width=STROKE * s)
    d.line([(40 * s, 43 * s), (40 * s, 58 * s)], fill=color, width=STROKE * s)
    return _finish(img)


def draw_orders(color) -> Image.Image:
    img = _canvas()
    d = ImageDraw.Draw(img)
    s = SCALE
    d.rounded_rectangle([(18 * s, 13 * s), (63 * s, 68 * s)], radius=8 * s, outline=color, width=STROKE * s)
    for y in (30, 43, 56):
        d.line([(26 * s, y * s), (55 * s, y * s)], fill=color, width=4 * s)
    return _finish(img)


def draw_profile(color) -> Image.Image:
    img = _canvas()
    d = ImageDraw.Draw(img)
    s = SCALE
    d.ellipse([(28 * s, 13 * s), (52 * s, 37 * s)], outline=color, width=STROKE * s)
    d.arc([(16 * s, 42 * s), (64 * s, 78 * s)], start=180, end=360, fill=color, width=STROKE * s)
    return _finish(img)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    specs = {
        "home": draw_home,
        "orders": draw_orders,
        "profile": draw_profile,
    }
    for name, draw in specs.items():
        draw(NORMAL).save(OUT_DIR / f"{name}.png")
        draw(ACTIVE).save(OUT_DIR / f"{name}-active.png")
        print(f"OK {name}.png / {name}-active.png")


if __name__ == "__main__":
    main()
