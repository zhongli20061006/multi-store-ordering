from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import ensure_store_access, get_current_user
from app.core import uploads
from app.core.database import get_db
from app.core.errors import BusinessError
from app.core.response import ok
from app.models import StoreBanner
from app.schemas.banner import BannerOut, BannerUpdate
from app.services.banner_service import create_banner, delete_banner, list_admin_banners, update_banner


router = APIRouter(prefix="/admin/stores/{store_id}/banners", tags=["admin"])


@router.get("")
def get_banners(store_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ensure_store_access(user, store_id)
    banners = list_admin_banners(db, store_id)
    return ok([BannerOut.model_validate(b).model_dump() for b in banners])


@router.post("", status_code=201)
async def post_banner(
    store_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ensure_store_access(user, store_id)
    content_type = request.headers.get("content-type", "")
    data = await request.body()
    url = uploads.save_banner_image(data, store_id, content_type)
    banner = create_banner(db, store_id, url)
    return ok(BannerOut.model_validate(banner).model_dump())


@router.put("/{banner_id}")
def put_banner(
    store_id: int,
    banner_id: int,
    payload: BannerUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ensure_store_access(user, store_id)
    banner = db.get(StoreBanner, banner_id)
    if banner is None or banner.store_id != store_id:
        raise BusinessError(404, "轮播图不存在")
    return ok(BannerOut.model_validate(update_banner(db, banner, payload)).model_dump())


@router.delete("/{banner_id}")
def delete_banner_endpoint(
    store_id: int, banner_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    ensure_store_access(user, store_id)
    banner = db.get(StoreBanner, banner_id)
    if banner is None or banner.store_id != store_id:
        raise BusinessError(404, "轮播图不存在")
    uploads.delete_image(banner.image_url)
    delete_banner(db, banner)
    return ok({"deleted": True})
