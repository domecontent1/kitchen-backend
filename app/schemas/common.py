# backend/app/schemas/common.py
from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str