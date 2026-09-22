# D:\Github\kitchen\backend\app\schemas\dish.py
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints


DishName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]

DishDescription = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=5, max_length=500)]

DishCategory = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2, max_length=50)]


class DishCreate(BaseModel):
    name: DishName
    description: DishDescription
    price: float = Field(gt=0)
    category: DishCategory


class DishUpdate(BaseModel):
    name: DishName
    description: DishDescription
    price: float = Field(gt=0)
    category: DishCategory


class DishResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    active: bool
    category: str
    image_url: Optional[str]