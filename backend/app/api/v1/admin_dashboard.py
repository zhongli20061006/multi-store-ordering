from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import ensure_store_access, get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.services.dashboard_service import store_dashboard


router = APIRouter(prefix="/admin/stores", tags=["admin"])


@router.get("/{store_id}/dashboard")
def get_dashboard(store_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ensure_store_access(user, store_id)
    return ok(store_dashboard(db, store_id))
