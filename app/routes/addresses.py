# backend/app/routes/addresses.py
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate
from app.schemas.common import MessageResponse
from app.services.address_service import address_service


router = APIRouter(prefix="/addresses", tags=["Addresses"])


def address_to_response(address: dict) -> dict:
    return {
        "id": str(address["_id"]),
        "label": address["label"],
        "address_line": address["address_line"],
        "landmark": address.get("landmark"),
        "town": address["town"],
        "pincode": address["pincode"],
        "active": address["active"]
    }


@router.post("/", response_model=AddressResponse)
async def create_address(
    address: AddressCreate,
    current_user: dict = Depends(get_current_user)):
    created_address = await address_service.create_address(user_id=str(current_user["_id"]),
        address_data=address.model_dump())

    return address_to_response(created_address)


@router.get("/", response_model=list[AddressResponse])
async def get_addresses(current_user: dict = Depends(get_current_user)):
    addresses = await address_service.get_user_addresses(
        user_id=str(current_user["_id"])
    )

    return [address_to_response(address) for address in addresses]


@router.get("/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: str,
    current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(address_id):
        raise HTTPException(status_code=400,
            detail="Invalid address ID")

    address = await address_service.get_address(address_id=address_id,
        user_id=str(current_user["_id"]))

    if address is None:
        raise HTTPException(status_code=404,
            detail="Address not found")

    return address_to_response(address)


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(address_id: str,address: AddressUpdate,
    current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(address_id):
        raise HTTPException(status_code=400,
            detail="Invalid address ID")

    updated_address = await address_service.update_address(
        address_id=address_id,
        user_id=str(current_user["_id"]),
        address_data=address.model_dump()
    )

    if updated_address is None:
        raise HTTPException(status_code=404,
            detail="Address not found")

    return address_to_response(updated_address)


@router.delete("/{address_id}", response_model=MessageResponse)
async def deactivate_address(
    address_id: str,
    current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(address_id):
        raise HTTPException(status_code=400,
            detail="Invalid address ID")

    matched_count = await address_service.deactivate_address(
        address_id=address_id,
        user_id=str(current_user["_id"]))

    if matched_count == 0:
        raise HTTPException(status_code=404,
            detail="Address not found")

    return {"message": "Address deactivated successfully"}