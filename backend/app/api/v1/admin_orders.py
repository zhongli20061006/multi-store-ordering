from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import BusinessError
from app.core.response import ok
from app.models import Order
from app.schemas.order import MerchantCancelRequest, OrderOut, OrderStatusUpdate, PaymentUpdate
from app.services.order_service import cancel_order, get_order, mark_order_paid, update_order_status
from app.api.v1.deps import ensure_store_access, get_current_user, get_user_store_ids


router = APIRouter(prefix="/admin/orders", tags=["admin"])


@router.get("")
def list_admin_orders(
    store_id: int | None = None,
    order_status: str | None = Query(default=None, pattern="^(pending|accepted|completed|cancelled)$"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    store_ids = get_user_store_ids(user)
    query = select(Order).where(Order.store_id.in_(store_ids))
    if store_id is not None:
        ensure_store_access(user, store_id)
        query = query.where(Order.store_id == store_id)
    if order_status is not None:
        query = query.where(Order.order_status == order_status)
    orders = list(db.scalars(query.order_by(Order.created_at.desc(), Order.id.desc())))
    return ok([OrderOut.model_validate(order).model_dump() for order in orders])


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
