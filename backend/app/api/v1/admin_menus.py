from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import BusinessError
from app.core.response import ok
from app.models import MenuCategory, MenuItem
from app.schemas.menu import CategoryCreate, CategoryOut, ItemCreate, ItemOut, ItemUpdate
from app.services.menu_service import (
    create_category,
    create_item,
    delete_category,
    delete_item,
    list_categories,
    list_items,
    update_category,
    update_item,
)
from app.api.v1.deps import ensure_store_access, get_current_user


router = APIRouter(prefix="/admin/stores/{store_id}", tags=["admin"])


@router.get("/categories")
def get_categories(store_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ensure_store_access(user, store_id)
    categories = list_categories(db, store_id)
    return ok([CategoryOut.model_validate(category).model_dump() for category in categories])


@router.post("/categories", status_code=201)
def post_category(store_id: int, payload: CategoryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ensure_store_access(user, store_id)
    category = create_category(db, store_id, payload)
    return ok(CategoryOut.model_validate(category).model_dump())


@router.put("/categories/{category_id}")
def put_category(
    store_id: int,
    category_id: int,
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ensure_store_access(user, store_id)
    category = db.get(MenuCategory, category_id)
    if category is None or category.store_id != store_id:
        raise BusinessError(404, "分类不存在")
    return ok(CategoryOut.model_validate(update_category(db, store_id, category, payload)).model_dump())


@router.delete("/categories/{category_id}")
def delete_category_endpoint(
    store_id: int, category_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    ensure_store_access(user, store_id)
    category = db.get(MenuCategory, category_id)
    if category is None or category.store_id != store_id:
        raise BusinessError(404, "分类不存在")
    delete_category(db, category)
    return ok({"deleted": True})


@router.get("/items")
def get_items(store_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ensure_store_access(user, store_id)
    items = list_items(db, store_id)
    return ok([ItemOut.model_validate(item).model_dump() for item in items])


@router.post("/items", status_code=201)
def post_item(store_id: int, payload: ItemCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ensure_store_access(user, store_id)
    item = create_item(db, store_id, payload)
    return ok(ItemOut.model_validate(item).model_dump())


@router.put("/items/{item_id}")
def put_item(
    store_id: int,
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ensure_store_access(user, store_id)
    item = db.get(MenuItem, item_id)
    if item is None or item.store_id != store_id:
        raise BusinessError(404, "商品不存在")
    return ok(ItemOut.model_validate(update_item(db, store_id, item, payload)).model_dump())


@router.delete("/items/{item_id}")
def delete_item_endpoint(
    store_id: int, item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    ensure_store_access(user, store_id)
    item = db.get(MenuItem, item_id)
    if item is None or item.store_id != store_id:
        raise BusinessError(404, "商品不存在")
    delete_item(db, item)
    return ok({"deleted": True})
