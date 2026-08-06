from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.models import Order, Store, StoreAdmin, User
from app.schemas.store import StoreCreate, StoreStatus, StoreUpdate


def list_public_stores(db: Session) -> list[Store]:
    return list(
        db.scalars(
            select(Store)
            .where(Store.status == StoreStatus.OPEN.value)
            .order_by(Store.sort_order, Store.id)
        )
    )


def get_store(db: Session, store_id: int) -> Store | None:
    return db.get(Store, store_id)


def list_admin_stores(db: Session, user: User) -> list[Store]:
    store_ids = [link.store_id for link in user.store_links]
    if not store_ids:
        return []
    return list(db.scalars(select(Store).where(Store.id.in_(store_ids)).order_by(Store.sort_order, Store.id)))


def _validate_hours(data) -> None:
    if data.open_time and data.close_time and data.open_time == data.close_time:
        raise BusinessError(400, "营业时间范围无效（开始与结束不能相同）")


def _validate_coords(data) -> None:
    if (data.latitude is None) != (data.longitude is None):
        raise BusinessError(400, "经纬度需同时填写")


def create_store(db: Session, data: StoreCreate, user: User) -> Store:
    _validate_hours(data)
    _validate_coords(data)
    store = Store(**data.model_dump())
    db.add(store)
    db.flush()
    db.add(StoreAdmin(store_id=store.id, user_id=user.id))
    db.commit()
    db.refresh(store)
    return store


def update_store(db: Session, store: Store, data: StoreUpdate) -> Store:
    _validate_hours(data)
    _validate_coords(data)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(store, field, value)
    db.commit()
    db.refresh(store)
    return store


def set_store_status(db: Session, store: Store, status: StoreStatus) -> Store:
    store.status = status.value
    db.commit()
    db.refresh(store)
    return store


def delete_store(db: Session, store: Store) -> None:
    has_orders = db.scalar(select(Order.id).where(Order.store_id == store.id).limit(1))
    if has_orders is not None:
        raise BusinessError(409, "该门店已有订单，不能删除")
    db.delete(store)
    db.commit()
