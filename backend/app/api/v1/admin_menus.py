from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core import uploads
from app.core.database import get_db
from app.core.errors import BusinessError
from app.core.response import ok
from app.models import MenuCategory, MenuItem
from app.schemas.menu import CategoryCreate, CategoryOut, ItemCreate, ItemOut, ItemUpdate
from app.services.menu_service import (
    clear_item_image,
    create_category,
    create_item,
    delete_category,
    delete_item,
    list_categories,
    list_items,
    set_item_image,
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


@router.post("/items/{item_id}/image")
async def upload_item_image(
    store_id: int,
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ensure_store_access(user, store_id)
    item = db.get(MenuItem, item_id)
    if item is None or item.store_id != store_id:
        raise BusinessError(404, "商品不存在")
    content_type = request.headers.get("content-type", "")
    data = await request.body()
    url = uploads.save_item_image(data, store_id, item_id, content_type)
    return ok(ItemOut.model_validate(set_item_image(db, item, url)).model_dump())


@router.delete("/items/{item_id}/image")
def clear_item_image_endpoint(
    store_id: int, item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    ensure_store_access(user, store_id)
    item = db.get(MenuItem, item_id)
    if item is None or item.store_id != store_id:
        raise BusinessError(404, "商品不存在")
    uploads.delete_image(item.image_url)
    return ok(ItemOut.model_validate(clear_item_image(db, item)).model_dump())
