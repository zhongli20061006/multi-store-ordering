# -*- coding: utf-8 -*-
"""商家数据看板：近 N 天（默认 7）按 Asia/Shanghai 自然日聚合。
口径：订单数 = 当日下单数（不含已取消）；营业额 = 已完成订单总额。"""
from datetime import datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Order

CN_TZ = timezone(timedelta(hours=8))
CN_OFFSET = timedelta(hours=8)


def store_dashboard(db: Session, store_id: int, days: int = 7) -> dict:
    local_today = datetime.now(CN_TZ).date()
    buckets = [local_today - timedelta(days=i) for i in range(days - 1, -1, -1)]
    first_local = datetime.combine(buckets[0], time.min, tzinfo=CN_TZ)
    since_utc = (first_local - CN_OFFSET).replace(tzinfo=None)
    rows = db.execute(
        select(Order.created_at, Order.order_status, Order.total_cents).where(
            Order.store_id == store_id, Order.created_at >= since_utc
        )
    ).all()
    stats = {d: {"order_count": 0, "revenue_cents": 0} for d in buckets}
    today_pending = 0
    today_completed = 0
    for created_at, status, total in rows:
        local_date = (created_at + CN_OFFSET).date()
        if local_date not in stats:
            continue
        if local_date == local_today:
            if status == "pending":
                today_pending += 1
            if status == "completed":
                today_completed += 1
        if status == "cancelled":
            continue
        stats[local_date]["order_count"] += 1
        if status == "completed":
            stats[local_date]["revenue_cents"] += total
    return {
        "daily": [
            {
                "date": d.strftime("%m-%d"),
                "order_count": stats[d]["order_count"],
                "revenue_cents": stats[d]["revenue_cents"],
            }
            for d in buckets
        ],
        "today": {
            "order_count": stats[local_today]["order_count"],
            "pending": today_pending,
            "completed": today_completed,
            "revenue_cents": stats[local_today]["revenue_cents"],
        },
    }
