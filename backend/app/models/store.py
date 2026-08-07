from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, utcnow


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    address: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str] = mapped_column(String(20))
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="open", index=True)
    open_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    close_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    admin_links: Mapped[list["StoreAdmin"]] = relationship(back_populates="store")  # noqa: F821
    categories: Mapped[list["MenuCategory"]] = relationship(back_populates="store")  # noqa: F821
    items: Mapped[list["MenuItem"]] = relationship(back_populates="store")  # noqa: F821
    orders: Mapped[list["Order"]] = relationship(back_populates="store")  # noqa: F821
    banners: Mapped[list["StoreBanner"]] = relationship(back_populates="store")  # noqa: F821


class StoreAdmin(Base):
    __tablename__ = "store_admins"

    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    store: Mapped["Store"] = relationship(back_populates="admin_links")  # noqa: F821
    user: Mapped["User"] = relationship(back_populates="store_links")  # noqa: F821
