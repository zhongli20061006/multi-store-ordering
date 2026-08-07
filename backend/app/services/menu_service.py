import json

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.models import MenuCategory, MenuItem, Store
from app.schemas.menu import CategoryCreate, ItemCreate, ItemUpdate


def get_menu(db: Session, store_id: int) -> list[MenuCategory]:
    categories = list(
        db.scalars(
            select(MenuCategory)
            .where(MenuCategory.store_id == store_id, MenuCategory.is_active.is_(True))
            .order_by(MenuCategory.sort_order, MenuCategory.id)
        )
    )
    items = list(
        db.scalars(
            select(MenuItem)
            .where(MenuItem.store_id == store_id, MenuItem.is_active.is_(True))
            .order_by(MenuItem.sort_order, MenuItem.id)
        )
    )
    for category in categories:
        category.items = [item for item in items if item.category_id == category.id]
    uncategorized = [item for item in items if item.category_id is None]
    if uncategorized:
        categories.append(
            MenuCategory(id=0, name="其他", sort_order=9999, store_id=store_id, is_active=True, items=uncategorized)
        )
    return categories


def _get_store(db: Session, store_id: int) -> Store:
    store = db.get(Store, store_id)
    if store is None:
        raise BusinessError(404, "门店不存在")
    return store


def _ensure_category_in_store(db: Session, store_id: int, category_id: int | None) -> None:
    if category_id is None:
        return
    category = db.get(MenuCategory, category_id)
    if category is None or category.store_id != store_id:
        raise BusinessError(400, "分类不存在或不属于该门店")


def list_categories(db: Session, store_id: int) -> list[MenuCategory]:
    _get_store(db, store_id)
    return list(
        db.scalars(
            select(MenuCategory).where(MenuCategory.store_id == store_id).order_by(MenuCategory.sort_order, MenuCategory.id)
        )
    )


def create_category(db: Session, store_id: int, data: CategoryCreate) -> MenuCategory:
    _get_store(db, store_id)
    category = MenuCategory(store_id=store_id, **data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, store_id: int, category: MenuCategory, data: CategoryCreate) -> MenuCategory:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: MenuCategory) -> None:
    category.is_active = False
    db.execute(
        update(MenuItem)
        .where(MenuItem.category_id == category.id, MenuItem.is_active.is_(True))
        .values(is_active=False)
    )
    db.commit()


def list_items(db: Session, store_id: int) -> list[MenuItem]:
    _get_store(db, store_id)
    return list(db.scalars(select(MenuItem).where(MenuItem.store_id == store_id).order_by(MenuItem.sort_order, MenuItem.id)))


def create_item(db: Session, store_id: int, data: ItemCreate) -> MenuItem:
    _get_store(db, store_id)
    _ensure_category_in_store(db, store_id, data.category_id)
    payload = data.model_dump()
    if payload.get("spec_groups") is not None:
        payload["spec_groups"] = json.dumps(payload["spec_groups"], ensure_ascii=False)
    item = MenuItem(store_id=store_id, **payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, store_id: int, item: MenuItem, data: ItemUpdate) -> MenuItem:
    _ensure_category_in_store(db, store_id, data.category_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "spec_groups" and value is not None:
            value = json.dumps(value, ensure_ascii=False)
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def set_item_image(db: Session, item: MenuItem, url: str) -> MenuItem:
    item.image_url = url
    db.commit()
    db.refresh(item)
    return item


def clear_item_image(db: Session, item: MenuItem) -> MenuItem:
    item.image_url = None
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: MenuItem) -> None:
    item.is_active = False
    db.commit()
