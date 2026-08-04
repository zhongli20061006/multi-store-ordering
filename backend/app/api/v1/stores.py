from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import BusinessError
from app.core.response import ok
from app.schemas.menu import MenuCategoryGroupOut
from app.schemas.store import StoreOut
from app.services.menu_service import get_menu
from app.services.store_service import get_store, list_public_stores


router = APIRouter(tags=["public"])


@router.get("/stores")
def list_stores(db: Session = Depends(get_db)):
    stores = list_public_stores(db)
    return ok([StoreOut.model_validate(store).model_dump() for store in stores])


@router.get("/stores/{store_id}/menu")
def store_menu(store_id: int, db: Session = Depends(get_db)):
    if get_store(db, store_id) is None:
        raise BusinessError(404, "门店不存在")
    groups = get_menu(db, store_id)
    return ok([MenuCategoryGroupOut.model_validate(group).model_dump() for group in groups])
