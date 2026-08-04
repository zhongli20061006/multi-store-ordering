from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import BusinessError
from app.core.response import ok
from app.schemas.store import StoreCreate, StoreOut, StoreStatusUpdate, StoreUpdate
from app.services.store_service import (
    create_store,
    delete_store,
    get_store,
    list_admin_stores,
    set_store_status,
    update_store,
)
from app.api.v1.deps import ensure_store_access, get_current_user


router = APIRouter(prefix="/admin/stores", tags=["admin"])


@router.get("")
def list_my_stores(db: Session = Depends(get_db), user=Depends(get_current_user)):
    stores = list_admin_stores(db, user)
    return ok([StoreOut.model_validate(store).model_dump() for store in stores])


@router.post("", status_code=201)
def create_store_endpoint(payload: StoreCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    store = create_store(db, payload, user)
    return ok(StoreOut.model_validate(store).model_dump())


@router.put("/{store_id}")
def update_store_endpoint(
    store_id: int, payload: StoreUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    ensure_store_access(user, store_id)
    store = get_store(db, store_id)
    if store is None:
        raise BusinessError(404, "门店不存在")
    return ok(StoreOut.model_validate(update_store(db, store, payload)).model_dump())


@router.patch("/{store_id}/status")
def set_store_status_endpoint(
    store_id: int, payload: StoreStatusUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    ensure_store_access(user, store_id)
    store = get_store(db, store_id)
    if store is None:
        raise BusinessError(404, "门店不存在")
    return ok(StoreOut.model_validate(set_store_status(db, store, payload.status)).model_dump())


@router.delete("/{store_id}")
def delete_store_endpoint(store_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ensure_store_access(user, store_id)
    store = get_store(db, store_id)
    if store is None:
        raise BusinessError(404, "门店不存在")
    delete_store(db, store)
    return ok({"deleted": True})
