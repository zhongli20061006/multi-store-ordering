import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.models import MenuItem, Order, OrderItem, Store
from app.schemas.order import CancelReason, OrderCreate, OrderEntryType, OrderStatus, PaymentStatus


ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.ACCEPTED},
    OrderStatus.ACCEPTED: {OrderStatus.SERVED},
    OrderStatus.SERVED: set(),
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}


# 中国无夏令时，固定 UTC+8 即 Asia/Shanghai（Windows 无 tzdata 时 ZoneInfo 不可用）
CN_TZ = timezone(timedelta(hours=8))


def _local_day_start_utc() -> datetime:
    """Asia/Shanghai 自然日零点对应的 UTC（落库时间为无时区 UTC）。"""
    local_now = datetime.now(CN_TZ)
    local_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    return local_midnight.astimezone(timezone.utc).replace(tzinfo=None)


def is_within_business_hours(open_time: str, close_time: str, now: datetime) -> bool:
    """营业区间 [open, close)，HH:MM，按本地自然日。"""
    now_t = now.time()
    open_t = datetime.strptime(open_time, "%H:%M").time()
    close_t = datetime.strptime(close_time, "%H:%M").time()
    return open_t <= now_t < close_t


def generate_order_no(db: Session, store_id: int) -> str:
    """4 位随机订单号；同门店当天不重复，隔天可复用。"""
    since = _local_day_start_utc()
    used = set(
        db.scalars(
            select(Order.order_no).where(
                Order.store_id == store_id,
                Order.created_at >= since,
            )
        )
    )
    for _ in range(100):
        candidate = f"{secrets.randbelow(9000) + 1000:04d}"
        if candidate not in used:
            return candidate
    raise BusinessError(409, "今日该门店订单号已用尽，请稍后再试")


def create_order(db: Session, payload: OrderCreate) -> tuple[Order, bool]:
    store = db.get(Store, payload.store_id)
    if store is None:
        raise BusinessError(404, "门店不存在")
    if store.status != "open":
        raise BusinessError(409, "门店已打烊，暂不可下单")
    if store.open_time and store.close_time:
        if not is_within_business_hours(store.open_time, store.close_time, datetime.now(CN_TZ)):
            raise BusinessError(409, f"门店当前未营业（营业时间 {store.open_time}-{store.close_time}）")

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

    # 库存预检：一次返回全部不足商品及当前可售量，便于前端自动修正
    insufficient = []
    for line in payload.items:
        item = item_map[line.menu_item_id]
        if item.stock is not None and line.quantity > item.stock:
            insufficient.append(
                {"menu_item_id": item.id, "name": item.name, "available_stock": item.stock}
            )
    if insufficient:
        raise BusinessError(409, "部分商品库存不足，请调整数量", detail={"insufficient_items": insufficient})

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
                category_name=item.category.name if item.category else None,
                unit_price_cents=item.price_cents,
                quantity=line.quantity,
                subtotal_cents=subtotal,
            )
        )

    order = Order(
        order_no=generate_order_no(db, payload.store_id),
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


def list_admin_orders(
    db: Session,
    store_ids: list[int],
    store_id: int | None = None,
    order_status: str | None = None,
    keyword: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> list[Order]:
    """商家订单列表（分页可选）：列表与 CSV 导出同口径（门店归属由调用方校验）。"""
    query = _apply_admin_order_filters(
        select(Order), store_ids, store_id, order_status, keyword, date_from, date_to
    )
    if page is not None and page_size is not None:
        query = query.offset((page - 1) * page_size).limit(page_size)
    return list(db.scalars(query.order_by(Order.created_at.desc(), Order.id.desc())))


def count_admin_orders(
    db: Session,
    store_ids: list[int],
    store_id: int | None = None,
    order_status: str | None = None,
    keyword: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> int:
    query = _apply_admin_order_filters(
        select(func.count(Order.id)), store_ids, store_id, order_status, keyword, date_from, date_to
    )
    return db.scalar(query) or 0


def _apply_admin_order_filters(
    query,
    store_ids: list[int],
    store_id: int | None,
    order_status: str | None,
    keyword: str | None,
    date_from: str | None,
    date_to: str | None,
):
    query = query.where(Order.store_id.in_(store_ids))
    if store_id is not None:
        query = query.where(Order.store_id == store_id)
    if order_status is not None:
        query = query.where(Order.order_status == order_status)
    if keyword and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.where(
            or_(Order.order_no.like(kw), Order.customer_phone.like(kw), Order.customer_name.like(kw))
        )
    start_utc, end_utc = _date_range_utc(date_from, date_to)
    if start_utc is not None:
        query = query.where(Order.created_at >= start_utc)
    if end_utc is not None:
        query = query.where(Order.created_at < end_utc)
    return query


def _date_range_utc(date_from: str | None, date_to: str | None) -> tuple[datetime | None, datetime | None]:
    """YYYY-MM-DD（UTC+8 自然日，含边界）→ UTC 无时区区间 [start, end)。"""
    if date_from is None and date_to is None:
        return None, None
    from_dt = _parse_date(date_from) if date_from else None
    to_dt = _parse_date(date_to) if date_to else None
    if from_dt is not None and to_dt is not None and from_dt > to_dt:
        raise BusinessError(422, "日期范围无效（开始不能晚于结束）")
    start_utc = (from_dt - timedelta(hours=8)) if from_dt is not None else None
    end_utc = (to_dt + timedelta(days=1) - timedelta(hours=8)) if to_dt is not None else None
    return start_utc, end_utc


def _parse_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise BusinessError(422, "日期格式无效（应为 YYYY-MM-DD）")


def get_store_order_stats(
    db: Session,
    store_ids: list[int],
    store_id: int | None = None,
) -> dict:
    """统计卡全量口径（不受列表筛选/分页影响）：
    today=今日下单数（含取消）；pending/completed=全量计数；revenue_today=今日已完成总额。"""
    scope = [store_id] if store_id is not None else store_ids
    today_start = _local_day_start_utc()
    today_rows = db.execute(
        select(Order.order_status, Order.total_cents).where(
            Order.store_id.in_(scope),
            Order.created_at >= today_start,
        )
    ).all()
    pending = db.scalar(
        select(func.count(Order.id)).where(Order.store_id.in_(scope), Order.order_status == "pending")
    )
    completed = db.scalar(
        select(func.count(Order.id)).where(Order.store_id.in_(scope), Order.order_status == "completed")
    )
    return {
        "today": len(today_rows),
        "pending": pending or 0,
        "completed": completed or 0,
        "revenue_today": sum(total for status, total in today_rows if status == "completed"),
    }


def update_order_status(db: Session, order: Order, new_status: OrderStatus) -> Order:
    current = OrderStatus(order.order_status)
    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise BusinessError(409, f"订单状态不允许从 {current.value} 变更为 {new_status.value}")
    order.order_status = new_status.value
    db.commit()
    db.refresh(order)
    return order


def mark_order_paid(db: Session, order: Order) -> Order:
    if order.order_status == OrderStatus.CANCELLED.value:
        raise BusinessError(409, "已取消的订单不能标记付款")
    order.payment_status = PaymentStatus.PAID.value
    db.commit()
    db.refresh(order)
    return order


def cancel_order(db: Session, order: Order, reason: CancelReason, actor_id: int | None) -> Order:
    if order.order_status == OrderStatus.CANCELLED.value:
        return order  # 幂等：已取消直接返回，不重复回补
    current = OrderStatus(order.order_status)
    if current not in (OrderStatus.PENDING, OrderStatus.ACCEPTED):
        raise BusinessError(409, "当前状态不可取消")
    if reason == CancelReason.CUSTOMER_CANCEL:
        if current != OrderStatus.PENDING:
            raise BusinessError(409, "已接单后顾客不能取消")
    elif reason not in (CancelReason.MERCHANT_CANCEL_NOT_MADE, CancelReason.MERCHANT_CANCEL_MADE):
        raise BusinessError(400, "取消原因不合法")
    order.order_status = OrderStatus.CANCELLED.value
    order.cancel_reason = reason.value
    order.cancel_by = actor_id
    if reason != CancelReason.MERCHANT_CANCEL_MADE:
        _restock_items(db, order)
    db.commit()
    db.refresh(order)
    return order


def pickup_order(db: Session, order: Order) -> Order:
    if order.order_status == OrderStatus.COMPLETED.value:
        return order  # 幂等：已完成直接返回
    current = OrderStatus(order.order_status)
    if current == OrderStatus.CANCELLED:
        raise BusinessError(409, "已取消的订单不能确认取单")
    if current != OrderStatus.SERVED:
        raise BusinessError(409, "出单后才能确认取单")
    order.order_status = OrderStatus.COMPLETED.value
    db.commit()
    db.refresh(order)
    return order


def _restock_items(db: Session, order: Order) -> None:
    for item in order.items:
        if item.menu_item_id is None:
            continue
        db.execute(
            update(MenuItem)
            .where(MenuItem.id == item.menu_item_id, MenuItem.stock.isnot(None))
            .values(stock=MenuItem.stock + item.quantity)
        )
