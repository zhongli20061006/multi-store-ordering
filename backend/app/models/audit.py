from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, utcnow


class AuditLog(Base):
    """订单操作审计：谁在何时对订单做了什么。
    - actor_type: merchant | customer（顾客无登录体系，actor_id 恒为 null，不用 0 魔法值）
    - detail: 结构化 JSON 文本，如 {"cancel_reason": "merchant_cancel_made", "prev_status": "pending"}
    - 索引：(order_id) 按单查；(store_id, created_at) 预留按门店查近 N 天操作日志
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_order_id", "order_id"),
        Index("ix_audit_logs_store_created", "store_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"))
    actor_type: Mapped[str] = mapped_column(String(16))
    actor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(32))
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
