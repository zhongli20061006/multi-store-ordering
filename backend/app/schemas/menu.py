import json

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SpecGroup(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    options: list[str] = Field(min_length=1, max_length=10)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True


class CategoryOut(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    description: str | None = Field(default=None, max_length=200)
    price_cents: int = Field(ge=1)
    spec_groups: list[SpecGroup] | None = None
    stock: int | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    category_id: int | None = None
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=60)
    description: str | None = Field(default=None, max_length=200)
    price_cents: int | None = Field(default=None, ge=1)
    spec_groups: list[SpecGroup] | None = None
    stock: int | None = Field(default=None, ge=0)
    category_id: int | None = None
    is_active: bool | None = None
    sort_order: int | None = Field(default=None, ge=0)


class ItemOut(ItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int

    @field_validator("spec_groups", mode="before")
    @classmethod
    def _parse_spec_groups(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            return json.loads(value) if value else None
        return value


class MenuCategoryGroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int
    items: list[ItemOut]
