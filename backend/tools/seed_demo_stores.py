# -*- coding: utf-8 -*-
"""扩展演示店铺为四家（四主题×四餐饮模式）：
中山路店=熟食(warm)、万达店=奶茶(white)、夜宵摊=夜宵(night)、甜品店=甜品(berry)。
幂等：按店名/分类名/商品名 upsert；中山路店旧饮品软下架。运行：python -m tools.seed_demo_stores"""
import json

from app.core.database import SessionLocal, init_db
from app.models import MenuCategory, MenuItem, Store, StoreAdmin, User
from sqlalchemy import select, update


def _specs(*groups):
    return json.dumps([{"name": name, "options": options} for name, options in groups], ensure_ascii=False)


DRINK_SPECS = _specs(("糖度", ["正常", "少糖", "多糖", "无糖"]), ("冰量", ["正常冰", "少冰", "多冰", "去冰"]))
HOT_SPECS = _specs(("辣度", ["不辣", "微辣", "中辣", "特辣"]))
SWEET_SPECS = _specs(("甜度", ["正常", "少糖", "半糖", "无糖"]), ("温度", ["常温", "冰", "热"]))


STORES = [
    {
        "name": "中山路店",
        "theme": "warm",
        "mode": "熟食",
        "address": "中山路 88 号",
        "phone": "0571-88880001",
        "lat": 30.2491,
        "lng": 120.1771,
        "admin": "admin1",
        "reset_menu": True,
        "categories": {
            "热餐": [
                ("招牌卤肉饭", 1800, None, HOT_SPECS),
                ("红烧牛腩饭", 2600, None, HOT_SPECS),
                ("台式香肠便当", 2000, None, HOT_SPECS),
            ],
            "卤味": [
                ("卤味拼盘", 2200, None, HOT_SPECS),
                ("招牌卤蛋", 300, None, None),
            ],
            "小吃": [
                ("现炸鸡腿", 1200, 20, None),
                ("关东煮套餐", 1500, None, HOT_SPECS),
            ],
            "汤品": [
                ("番茄蛋花汤", 800, None, None),
            ],
        },
    },
    {
        "name": "万达店",
        "theme": "white",
        "mode": "奶茶",
        "address": "万达广场 B1 层",
        "phone": "0571-88880002",
        "lat": 30.3299,
        "lng": 120.1599,
        "admin": "admin2",
        "reset_menu": False,
        "categories": {
            "招牌茶饮": [
                ("招牌奶茶", 1200, None, DRINK_SPECS),
                ("每日限量奶昔", 1800, 5, DRINK_SPECS),
                ("芋泥波波", 1500, 15, DRINK_SPECS),
            ],
            "果茶": [
                ("满杯百香果", 1000, None, DRINK_SPECS),
                ("柠檬红茶", 1200, None, DRINK_SPECS),
            ],
            "咖啡": [
                ("生椰拿铁", 1600, None, DRINK_SPECS),
                ("抹茶拿铁", 1700, None, DRINK_SPECS),
            ],
            "小食": [
                ("手工曲奇", 900, None, None),
            ],
        },
    },
    {
        "name": "夜宵摊",
        "theme": "night",
        "mode": "夜宵",
        "address": "河坊街夜市 12 号",
        "phone": "0571-88880003",
        "lat": 30.2426,
        "lng": 120.1689,
        "admin": "admin1",
        "reset_menu": False,
        "categories": {
            "烤串": [
                ("羊肉串（5串）", 2500, 30, HOT_SPECS),
                ("烤鸡翅（4只）", 2200, None, HOT_SPECS),
                ("蒜蓉烤茄子", 1500, None, HOT_SPECS),
            ],
            "炸物": [
                ("炸鸡架", 1800, None, HOT_SPECS),
                ("香辣小龙虾（份）", 6800, 10, HOT_SPECS),
            ],
            "主食": [
                ("炒米粉", 1600, None, HOT_SPECS),
            ],
            "饮品": [
                ("冰镇酸梅汤", 800, None, None),
            ],
        },
    },
    {
        "name": "甜品店",
        "theme": "berry",
        "mode": "甜品",
        "address": "湖滨路 36 号",
        "phone": "0571-88880004",
        "lat": 30.2556,
        "lng": 120.1611,
        "admin": "admin2",
        "reset_menu": False,
        "categories": {
            "蛋糕": [
                ("草莓奶油蛋糕（切件）", 2800, None, None),
                ("提拉米苏", 2600, None, None),
            ],
            "布丁糖水": [
                ("芒果布丁", 1500, None, None),
                ("双皮奶", 1200, None, None),
                ("芋圆红豆沙", 1600, None, SWEET_SPECS),
            ],
            "特调": [
                ("杨枝甘露", 1800, None, SWEET_SPECS),
                ("柠檬气泡水", 1200, None, SWEET_SPECS),
            ],
        },
    },
]


def _get_or_create_store(db, spec) -> Store:
    store = db.scalar(select(Store).where(Store.name == spec["name"]))
    if store is None:
        store = Store(
            name=spec["name"],
            address=spec["address"],
            phone=spec["phone"],
            sort_order=len(db.scalars(select(Store)).all()) + 1,
            latitude=spec["lat"],
            longitude=spec["lng"],
            theme=spec["theme"],
        )
        db.add(store)
        db.flush()
    else:
        store.theme = spec["theme"]
        store.address = spec["address"]
        store.phone = spec["phone"]
        store.latitude = spec["lat"]
        store.longitude = spec["lng"]
    admin = db.scalar(select(User).where(User.username == spec["admin"]))
    if admin is not None and not db.scalar(
        select(StoreAdmin).where(StoreAdmin.store_id == store.id, StoreAdmin.user_id == admin.id)
    ):
        db.add(StoreAdmin(store_id=store.id, user_id=admin.id))
    return store


def _sync_menu(db, store: Store, spec: dict) -> None:
    if spec.get("reset_menu"):
        db.execute(update(MenuCategory).where(MenuCategory.store_id == store.id).values(is_active=False))
        db.execute(update(MenuItem).where(MenuItem.store_id == store.id).values(is_active=False))
    sort = 0
    for cat_name, items in spec["categories"].items():
        sort += 1
        category = db.scalar(
            select(MenuCategory).where(MenuCategory.store_id == store.id, MenuCategory.name == cat_name)
        )
        if category is None:
            category = MenuCategory(store_id=store.id, name=cat_name, sort_order=sort, is_active=True)
            db.add(category)
            db.flush()
        else:
            category.is_active = True
            category.sort_order = sort
        item_sort = 0
        for name, price, stock, specs in items:
            item_sort += 1
            item = db.scalar(select(MenuItem).where(MenuItem.store_id == store.id, MenuItem.name == name))
            if item is None:
                db.add(
                    MenuItem(
                        store_id=store.id,
                        category_id=category.id,
                        name=name,
                        price_cents=price,
                        stock=stock,
                        spec_groups=specs,
                        sort_order=item_sort,
                        is_active=True,
                    )
                )
            else:
                item.category_id = category.id
                item.price_cents = price
                item.stock = stock
                item.spec_groups = specs
                item.sort_order = item_sort
                item.is_active = True
    allowed = set(spec["categories"].keys())
    for category in db.scalars(select(MenuCategory).where(MenuCategory.store_id == store.id)).all():
        if category.name not in allowed:
            category.is_active = False


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        for spec in STORES:
            store = _get_or_create_store(db, spec)
            _sync_menu(db, store, spec)
            print(f"OK {store.name}（{spec['mode']}/{spec['theme']}）")
        db.commit()
    finally:
        db.close()
    print("ALL_DONE")


if __name__ == "__main__":
    main()
