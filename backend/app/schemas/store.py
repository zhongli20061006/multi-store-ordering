from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StoreStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class StoreBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    address: str = Field(min_length=1, max_length=200)
    phone: str = Field(min_length=1, max_length=20)
    sort_order: int = Field(default=0, ge=0)


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    address: str | None = Field(default=None, min_length=1, max_length=200)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    sort_order: int | None = Field(default=None, ge=0)


class StoreOut(StoreBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StoreStatus


class StoreStatusUpdate(BaseModel):
    status: StoreStatus
