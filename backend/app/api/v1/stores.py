from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import BusinessError
from app.core.response import ok
from app.schemas.menu import MenuCategoryGroupOut
from app.schemas.store import StoreOut
from app.services.banner_service import list_public_banners
from app.services.menu_service import get_menu
from app.services.store_service import get_store, list_public_stores


router = APIRouter(tags=["public"])


@router.get("/stores")
def list_stores(db: Session = Depends(get_db)):
    stores = list_public_stores(db)
    return ok([StoreOut.model_validate(store).model_dump() for store in stores])


@router.get("/stores/{store_id}")
def get_store_detail(store_id: int, db: Session = Depends(get_db)):
    """公开单店信息：任意营业状态均返回（历史订单门店可能已打烊，导航仍可用）。"""
    store = get_store(db, store_id)
    if store is None:
        raise BusinessError(404, "门店不存在")
    return ok(StoreOut.model_validate(store).model_dump())


@router.get("/stores/{store_id}/banners")
def store_banners(store_id: int, db: Session = Depends(get_db)):
    if get_store(db, store_id) is None:
        raise BusinessError(404, "门店不存在")
    banners = list_public_banners(db, store_id)
    return ok([{"id": b.id, "image_url": b.image_url} for b in banners])


@router.get("/stores/{store_id}/menu")
def store_menu(store_id: int, db: Session = Depends(get_db)):
    if get_store(db, store_id) is None:
        raise BusinessError(404, "门店不存在")
    groups = get_menu(db, store_id)
    return ok([MenuCategoryGroupOut.model_validate(group).model_dump() for group in groups])
