import secrets
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.models import MenuItem, Order, OrderItem, Store
from app.schemas.order import OrderCreate, OrderEntryType, OrderStatus, PaymentStatus


ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.ACCEPTED, OrderStatus.CANCELLED},
    OrderStatus.ACCEPTED: {OrderStatus.COMPLETED, OrderStatus.CANCELLED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}


def generate_order_no() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}{secrets.randbelow(1_000_000):06d}"


def create_order(db: Session, payload: OrderCreate) -> tuple[Order, bool]:
    store = db.get(Store, payload.store_id)
    if store is None:
        raise BusinessError(404, "门店不存在")
    if store.status != "open":
        raise BusinessError(409, "门店已打烊，暂不可下单")

    existing = db.scalar(select(Order).where(Order.idempotency_key == payload.idempotency_key))
    if existing is not None:
        return existing, False

    item_ids = [line.menu_item_id for line in payload.items]
    if len(set(item_ids)) != len(item_ids):
        raise BusinessError(400, "同一商品请合并数量后再提交")

    items = list(
        db.scalars(
            select(MenuItem).where(
                MenuItem.id.in_(item_ids),
                MenuItem.store_id == payload.store_id,
                MenuItem.is_active.is_(True),
            )
        )
    )
    item_map = {item.id: item for item in items}
    missing = set(item_ids) - set(item_map)
    if missing:
        raise BusinessError(400, "部分商品不存在或已下架")

    total_cents = 0
    item_count = 0
    order_items: list[OrderItem] = []
    for line in payload.items:
        item = item_map[line.menu_item_id]
        if item.stock is not None:
            result = db.execute(
                update(MenuItem)
                .where(MenuItem.id == item.id, MenuItem.stock >= line.quantity)
                .values(stock=MenuItem.stock - line.quantity)
            )
            if result.rowcount == 0:
                raise BusinessError(409, f"商品「{item.name}」库存不足")
        subtotal = item.price_cents * line.quantity
        total_cents += subtotal
        item_count += line.quantity
        order_items.append(
            OrderItem(
                menu_item_id=item.id,
                item_name=item.name,
                unit_price_cents=item.price_cents,
                quantity=line.quantity,
                subtotal_cents=subtotal,
            )
        )

    order = Order(
        order_no=generate_order_no(),
        store_id=payload.store_id,
        entry_type=payload.entry_type.value,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        remark=payload.remark,
        item_count=item_count,
        total_cents=total_cents,
        idempotency_key=payload.idempotency_key,
    )
    db.add(order)
    db.flush()
    for order_item in order_items:
        order_item.order_id = order.id
        db.add(order_item)
    db.commit()
    db.refresh(order)
    return order, True


def get_order(db: Session, order_id: int) -> Order | None:
    return db.get(Order, order_id)


def update_order_status(db: Session, order: Order, new_status: OrderStatus) -> Order:
    current = OrderStatus(order.status)
    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise BusinessError(409, f"订单状态不允许从 {current.value} 变更为 {new_status.value}")
    order.status = new_status.value
    db.commit()
    db.refresh(order)
    return order


def mark_order_paid(db: Session, order: Order) -> Order:
    if order.status == OrderStatus.CANCELLED.value:
        raise BusinessError(409, "已取消的订单不能标记付款")
    order.payment_status = PaymentStatus.PAID.value
    db.commit()
    db.refresh(order)
    return order
