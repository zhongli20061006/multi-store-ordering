import csv
import io
import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.api.v1.deps import ensure_store_access, get_current_user, get_user_store_ids
from app.core.csv_utils import csv_safe, format_local
from app.core.database import get_db
from app.core.response import ok
from app.services.order_service import count_audit_logs, list_audit_logs


router = APIRouter(prefix="/admin/audit-logs", tags=["admin"])

AUDIT_ACTION_TEXT = {
    "accepted": "接单",
    "served": "出单",
    "cancelled": "取消",
    "paid": "标记付款",
    "customer_cancelled": "顾客取消",
    "customer_pickup": "顾客取单",
}
ACTOR_TEXT = {"merchant": "商家", "customer": "顾客"}


@router.get("")
def list_admin_audit_logs(
    store_id: int | None = None,
    date_from: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    date_to: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    store_ids = get_user_store_ids(user)
    if store_id is not None:
        ensure_store_access(user, store_id)
    rows = list_audit_logs(db, store_ids, store_id, date_from, date_to, page, page_size)
    total = count_audit_logs(db, store_ids, store_id, date_from, date_to)
    payload = []
    for log, order_no, store_name in rows:
        payload.append(
            {
                "id": log.id,
                "order_id": log.order_id,
                "order_no": order_no,
                "store_id": log.store_id,
                "store_name": store_name,
                "action": log.action,
                "actor_type": log.actor_type,
                "actor_id": log.actor_id,
                "detail": json.loads(log.detail) if log.detail else None,
                "created_at": log.created_at,
            }
        )
    return ok({"items": payload, "total": total})


@router.get("/export")
def export_admin_audit_logs(
    store_id: int | None = None,
    date_from: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    date_to: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    store_ids = get_user_store_ids(user)
    if store_id is not None:
        ensure_store_access(user, store_id)
    rows = list_audit_logs(db, store_ids, store_id, date_from, date_to)
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(["时间", "订单号", "门店", "动作", "操作方", "详情", "操作人ID"])
    for log, order_no, store_name in rows:
        writer.writerow(
            [
                format_local(log.created_at),
                order_no,
                store_name,
                AUDIT_ACTION_TEXT.get(log.action, log.action),
                ACTOR_TEXT.get(log.actor_type, log.actor_type),
                csv_safe(log.detail or ""),
                log.actor_id if log.actor_id is not None else "",
            ]
        )
    content = "\ufeff" + buffer.getvalue()
    return StreamingResponse(
        iter([content.encode("utf-8")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="audit-logs.csv"'},
    )
