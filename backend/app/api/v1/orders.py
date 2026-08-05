from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import BusinessError
from app.core.response import ok
from app.models import Order
from app.schemas.order import CancelReason, CustomerCancelRequest, OrderCreate, OrderOut
from app.services.order_service import cancel_order, create_order


router = APIRouter(tags=["public"])


@router.post("/orders", status_code=201)
def create_order_endpoint(payload: OrderCreate, db: Session = Depends(get_db)):
    order, _created = create_order(db, payload)
    return ok(OrderOut.model_validate(order).model_dump())


@router.post("/orders/{order_no}/cancel")
def customer_cancel(order_no: str, payload: CustomerCancelRequest, db: Session = Depends(get_db)):
    order = db.scalar(select(Order).where(Order.order_no == order_no).order_by(Order.id.desc()))
    if order is None or order.customer_phone != payload.phone:
        raise BusinessError(404, "订单不存在")
    return ok(OrderOut.model_validate(cancel_order(db, order, CancelReason.CUSTOMER_CANCEL, 0)).model_dump())


@router.get("/orders")
def get_my_order(
    phone: str = Query(pattern=r"^1[3-9]\d{9}$"),
    order_no: str = Query(min_length=4, max_length=32),
    db: Session = Depends(get_db),
):
    order = db.scalar(
        select(Order)
        .where(Order.order_no == order_no, Order.customer_phone == phone)
        .order_by(Order.id.desc())
    )
    if order is None:
        raise BusinessError(404, "订单不存在")
    return ok(OrderOut.model_validate(order).model_dump())
