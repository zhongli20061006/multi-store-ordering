"""初始化本地数据库与演示数据（幂等）。运行：python seed.py"""
from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.models import MenuCategory, MenuItem, Store, StoreAdmin, User


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        if db.scalar(select(User).limit(1)) is not None:
            print("数据库已有数据，跳过种子（如需重置请删除 data/ordering.db 后重跑）")
            return

        password = hash_password(settings.seed_admin_password)
        admin1 = User(username="admin1", password_hash=password, display_name="中山路店长")
        admin2 = User(username="admin2", password_hash=password, display_name="万达店长")
        db.add_all([admin1, admin2])
        db.flush()

        store1 = Store(name="中山路店", address="中山路 88 号", phone="0571-88880001", sort_order=1, open_time="09:00", close_time="22:00")
        store2 = Store(name="万达店", address="万达广场 B1 层", phone="0571-88880002", sort_order=2, open_time="09:00", close_time="22:00")
        db.add_all([store1, store2])
        db.flush()

        db.add_all(
            [
                StoreAdmin(store_id=store1.id, user_id=admin1.id),
                StoreAdmin(store_id=store2.id, user_id=admin2.id),
            ]
        )

        cat1 = MenuCategory(store_id=store1.id, name="招牌饮品", sort_order=1)
        cat2 = MenuCategory(store_id=store1.id, name="清爽果茶", sort_order=2)
        cat3 = MenuCategory(store_id=store2.id, name="招牌饮品", sort_order=1)
        db.add_all([cat1, cat2, cat3])
        db.flush()

        db.add_all(
            [
                MenuItem(store_id=store1.id, category_id=cat1.id, name="招牌奶茶", price_cents=1200, sort_order=1),
                MenuItem(store_id=store1.id, category_id=cat1.id, name="每日限量奶昔", price_cents=1800, stock=5, sort_order=2),
                MenuItem(store_id=store1.id, category_id=cat2.id, name="满杯百香果", price_cents=1000, sort_order=1),
                MenuItem(store_id=store2.id, category_id=cat3.id, name="招牌奶茶", price_cents=1300, sort_order=1),
                MenuItem(store_id=store2.id, category_id=cat3.id, name="生椰拿铁", price_cents=1600, sort_order=2),
            ]
        )
        db.commit()
        print(
            f"种子完成：门店 2 家，管理员 admin1/admin2（密码 {settings.seed_admin_password}）。"
            f"\nadmin1 → 中山路店，admin2 → 万达店"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
