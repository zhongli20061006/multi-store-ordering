from pydantic import BaseModel, ConfigDict, Field


class BannerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    store_id: int
    image_url: str
    sort_order: int
    is_active: bool


class BannerUpdate(BaseModel):
    sort_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
