from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, utcnow


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True)
    customer_name: Mapped[str] = mapped_column(String(30))
    customer_phone: Mapped[str] = mapped_column(String(20), index=True)
    remark: Mapped[str | None] = mapped_column(String(200), nullable=True)
    entry_type: Mapped[str] = mapped_column(String(16), default="preorder")
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    total_cents: Mapped[int] = mapped_column(Integer, default=0)
    order_status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    payment_status: Mapped[str] = mapped_column(String(16), default="unpaid")
    cancel_reason: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cancel_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="wechat_miniprogram")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    store: Mapped["Store"] = relationship(back_populates="orders")  # noqa: F821
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", order_by="OrderItem.id")  # noqa: F821


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    menu_item_id: Mapped[int | None] = mapped_column(ForeignKey("menu_items.id"), nullable=True)
    item_name: Mapped[str] = mapped_column(String(60))
    unit_price_cents: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    subtotal_cents: Mapped[int] = mapped_column(Integer)

    order: Mapped["Order"] = relationship(back_populates="items")  # noqa: F821
