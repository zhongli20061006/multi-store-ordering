from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.models import Store, StoreBanner
from app.schemas.banner import BannerUpdate


def _get_store(db: Session, store_id: int) -> None:
    if db.get(Store, store_id) is None:
        raise BusinessError(404, "门店不存在")


def list_admin_banners(db: Session, store_id: int) -> list[StoreBanner]:
    _get_store(db, store_id)
    return list(
        db.scalars(
            select(StoreBanner)
            .where(StoreBanner.store_id == store_id)
            .order_by(StoreBanner.sort_order, StoreBanner.id)
        )
    )


def list_public_banners(db: Session, store_id: int) -> list[StoreBanner]:
    return list(
        db.scalars(
            select(StoreBanner)
            .where(StoreBanner.store_id == store_id, StoreBanner.is_active.is_(True))
            .order_by(StoreBanner.sort_order, StoreBanner.id)
        )
    )


def create_banner(db: Session, store_id: int, image_url: str) -> StoreBanner:
    _get_store(db, store_id)
    max_sort = db.scalar(
        select(StoreBanner.sort_order).where(StoreBanner.store_id == store_id).order_by(StoreBanner.sort_order.desc()).limit(1)
    )
    banner = StoreBanner(store_id=store_id, image_url=image_url, sort_order=(max_sort or 0) + 1)
    db.add(banner)
    db.commit()
    db.refresh(banner)
    return banner


def update_banner(db: Session, banner: StoreBanner, data: BannerUpdate) -> StoreBanner:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(banner, field, value)
    db.commit()
    db.refresh(banner)
    return banner


def delete_banner(db: Session, banner: StoreBanner) -> None:
    db.delete(banner)
    db.commit()
