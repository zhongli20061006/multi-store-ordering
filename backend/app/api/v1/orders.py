from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok
from app.models import Order
from app.schemas.order import OrderCreate, OrderOut
from app.services.order_service import create_order


router = APIRouter(tags=["public"])


@router.post("/orders", status_code=201)
def create_order_endpoint(payload: OrderCreate, db: Session = Depends(get_db)):
    order, _created = create_order(db, payload)
    return ok(OrderOut.model_validate(order).model_dump())


@router.get("/orders")
def my_orders(phone: str = Query(pattern=r"^1[3-9]\d{9}$"), db: Session = Depends(get_db)):
    orders = list(
        db.scalars(select(Order).where(Order.customer_phone == phone).order_by(Order.created_at.desc(), Order.id.desc()))
    )
    return ok([OrderOut.model_validate(order).model_dump() for order in orders])
