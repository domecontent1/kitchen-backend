# app/schemas/dish.py

from pydantic import BaseModel, Field


class DishCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )
    description: str = Field(
        min_length=5,
        max_length=500
    )
    price: float = Field(
        gt=0
    )


class DishUpdate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )
    description: str = Field(
        min_length=5,
        max_length=500
    )
    price: float = Field(
        gt=0
    )


class DishResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    active: bool