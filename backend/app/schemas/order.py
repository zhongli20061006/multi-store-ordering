from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class OrderEntryType(str, Enum):
    PREORDER = "preorder"
    DINEIN = "dinein"


class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    SERVED = "served"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"


class CancelReason(str, Enum):
    CUSTOMER_CANCEL = "customer_cancel"
    MERCHANT_CANCEL_NOT_MADE = "merchant_cancel_not_made"
    MERCHANT_CANCEL_MADE = "merchant_cancel_made"


class CustomerPhoneRequest(BaseModel):
    phone: str = Field(pattern=r"^1[3-9]\d{9}$")


class MerchantCancelRequest(BaseModel):
    cancel_reason: CancelReason


class OrderItemInput(BaseModel):
    menu_item_id: int
    quantity: int = Field(ge=1, le=99)


class OrderCreate(BaseModel):
    store_id: int
    entry_type: OrderEntryType = OrderEntryType.PREORDER
    customer_name: str = Field(min_length=1, max_length=30)
    customer_phone: str = Field(pattern=r"^1[3-9]\d{9}$")
    remark: str | None = Field(default=None, max_length=200)
    idempotency_key: str = Field(min_length=8, max_length=64)
    items: list[OrderItemInput] = Field(min_length=1, max_length=50)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_item_id: int | None
    item_name: str
    category_name: str | None
    unit_price_cents: int
    quantity: int
    subtotal_cents: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_no: str
    store_id: int
    entry_type: OrderEntryType
    customer_name: str
    customer_phone: str
    remark: str | None
    item_count: int
    total_cents: int
    order_status: OrderStatus
    payment_status: PaymentStatus
    cancel_reason: CancelReason | None
    cancel_by: int | None
    source: str
    created_at: object
    items: list[OrderItemOut]


class OrderStatusUpdate(BaseModel):
    order_status: OrderStatus


class PaymentUpdate(BaseModel):
    payment_status: PaymentStatus
