from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StoreStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class StoreTheme(str, Enum):
    WARM = "warm"
    WHITE = "white"
    GREEN = "green"
    BERRY = "berry"


class StoreBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    address: str = Field(min_length=1, max_length=200)
    phone: str = Field(min_length=1, max_length=20)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    theme: StoreTheme = StoreTheme.WARM
    sort_order: int = Field(default=0, ge=0)
    open_time: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    close_time: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    address: str | None = Field(default=None, min_length=1, max_length=200)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    theme: StoreTheme | None = None
    sort_order: int | None = Field(default=None, ge=0)
    open_time: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    close_time: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")


class StoreOut(StoreBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StoreStatus
    image_url: str | None = None


class StoreStatusUpdate(BaseModel):
    status: StoreStatus
