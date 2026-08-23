# app/schemas/address.py
from pydantic import BaseModel, Field


class AddressCreate(BaseModel):
    label: str = Field(
        min_length=1,
        max_length=50
    )

    address_line: str = Field(
        min_length=5,
        max_length=250
    )

    landmark: str | None = Field(
        default=None,
        max_length=150
    )

    town: str = Field(
        min_length=2,
        max_length=100
    )

    pincode: str = Field(
        pattern=r"^[1-9]\d{5}$"
    )


class AddressUpdate(BaseModel):
    label: str = Field(
        min_length=1,
        max_length=50
    )

    address_line: str = Field(
        min_length=5,
        max_length=250
    )

    landmark: str | None = Field(
        default=None,
        max_length=150
    )

    town: str = Field(
        min_length=2,
        max_length=100
    )

    pincode: str = Field(
        pattern=r"^[1-9]\d{5}$"
    )


class AddressResponse(BaseModel):
    id: str
    label: str
    address_line: str
    landmark: str | None
    town: str
    pincode: str
    active: bool