import csv
import io

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.core.database import get_db
from app.core.errors import BusinessError
from app.core.response import ok
from app.models import Order, Store
from app.schemas.order import MerchantCancelRequest, OrderOut, OrderStatusUpdate, PaymentUpdate
from app.services.order_service import (
    CN_TZ,
    cancel_order,
    count_admin_orders,
    get_order,
    get_store_order_stats,
    list_admin_orders,
    mark_order_paid,
    update_order_status,
)
from app.api.v1.deps import ensure_store_access, get_current_user, get_user_store_ids


router = APIRouter(prefix="/admin/orders", tags=["admin"])


def mask_phone(phone: str) -> str:
    return f"{phone[:3]}****{phone[-4:]}" if len(phone) == 11 else phone


ORDER_STATUS_PATTERN = "^(pending|accepted|served|completed|cancelled)$"
STATUS_TEXT = {
    "pending": "待接单",
    "accepted": "已接单",
    "served": "已出单",
    "completed": "已完成",
    "cancelled": "已取消",
}
PAYMENT_TEXT = {"unpaid": "未付款", "paid": "已付款"}
ENTRY_TEXT = {"preorder": "提前点单", "dinein": "到店点单"}


def _csv_safe(value) -> str:
    """CSV 公式注入防护：以 = + - @ 或 Tab/CR 开头的单元格前置单引号。"""
    if value is None:
        return ""
    text = str(value)
    if text[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + text
    return text


def _format_local(dt) -> str:
    """落库时间为无时区 UTC，转 UTC+8 后格式化。"""
    offset = CN_TZ.utcoffset(None)
    return (dt + offset).strftime("%Y-%m-%d %H:%M:%S")


@router.get("")
def list_orders(
    store_id: int | None = None,
    order_status: str | None = Query(default=None, pattern=ORDER_STATUS_PATTERN),
    keyword: str | None = Query(default=None, max_length=60),
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
    orders = list_admin_orders(db, store_ids, store_id, order_status, keyword, date_from, date_to, page, page_size)
    total = count_admin_orders(db, store_ids, store_id, order_status, keyword, date_from, date_to)
    stats = get_store_order_stats(db, store_ids, store_id)
    payload = []
    for order in orders:
        data = OrderOut.model_validate(order).model_dump()
        data["customer_phone"] = mask_phone(data["customer_phone"])
        payload.append(data)
    return ok({"items": payload, "total": total, "stats": stats})


@router.get("/export")
def export_admin_orders(
    store_id: int | None = None,
    order_status: str | None = Query(default=None, pattern=ORDER_STATUS_PATTERN),
    keyword: str | None = Query(default=None, max_length=60),
    date_from: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    date_to: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    store_ids = get_user_store_ids(user)
    if store_id is not None:
        ensure_store_access(user, store_id)
    orders = list_admin_orders(db, store_ids, store_id, order_status, keyword, date_from, date_to)
    store_names = {s.id: s.name for s in db.scalars(select(Store).where(Store.id.in_(store_ids)))}
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(
        ["订单号", "下单时间", "门店", "入口类型", "顾客姓名", "联系电话", "件数", "金额(元)", "订单状态", "支付状态", "备注"]
    )
    for order in orders:
        writer.writerow(
            [
                order.order_no,
                _format_local(order.created_at),
                store_names.get(order.store_id, ""),
                ENTRY_TEXT.get(order.entry_type, order.entry_type),
                _csv_safe(order.customer_name),
                mask_phone(order.customer_phone),
                order.item_count,
                f"{order.total_cents / 100:.2f}",
                STATUS_TEXT.get(order.order_status, order.order_status),
                PAYMENT_TEXT.get(order.payment_status, order.payment_status),
                _csv_safe(order.remark),
            ]
        )
    content = "\ufeff" + buffer.getvalue()
    return StreamingResponse(
        iter([content.encode("utf-8")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="orders.csv"'},
    )


@router.get("/{order_id}")
def admin_order_detail(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = get_order(db, order_id)
    if order is None:
        raise BusinessError(404, "订单不存在")
    ensure_store_access(user, order.store_id)
    return ok(OrderOut.model_validate(order).model_dump())


@router.patch("/{order_id}/status")
def admin_update_order_status(
    order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    order = get_order(db, order_id)
    if order is None:
        raise BusinessError(404, "订单不存在")
    ensure_store_access(user, order.store_id)
    return ok(OrderOut.model_validate(update_order_status(db, order, payload.order_status)).model_dump())


@router.post("/{order_id}/cancel")
def admin_cancel(order_id: int, payload: MerchantCancelRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = get_order(db, order_id)
    if order is None:
        raise BusinessError(404, "订单不存在")
    ensure_store_access(user, order.store_id)
    if payload.cancel_reason.value == "customer_cancel":
        raise BusinessError(400, "商家取消原因不合法")
    return ok(OrderOut.model_validate(cancel_order(db, order, payload.cancel_reason, user.id)).model_dump())


@router.patch("/{order_id}/payment")
def admin_mark_paid(
    order_id: int, payload: PaymentUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    order = get_order(db, order_id)
    if order is None:
        raise BusinessError(404, "订单不存在")
    ensure_store_access(user, order.store_id)
    if payload.payment_status.value != "paid":
        raise BusinessError(400, "本阶段仅支持标记为已付款")
    return ok(OrderOut.model_validate(mark_order_paid(db, order)).model_dump())
