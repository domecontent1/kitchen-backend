from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import HTTPException

from app.core.delivery_config import AVAILABLE_DELIVERY_SLOTS


class DeliveryService:

    BUSINESS_TIMEZONE = ZoneInfo("Asia/Kolkata")

    def get_current_business_datetime(self) -> datetime:
        return datetime.now(self.BUSINESS_TIMEZONE)

    def validate_delivery_date(
        self,
        delivery_date: date
    ) -> None:

        today = self.get_current_business_datetime().date()

        maximum_date = today + timedelta(days=7)

        if delivery_date < today:
            raise HTTPException(
                status_code=400,
                detail="Delivery date cannot be in the past"
            )

        if delivery_date > maximum_date:
            raise HTTPException(
                status_code=400,
                detail="Delivery date can only be booked up to 7 days ahead"
            )

    def validate_delivery_slot(
        self,
        delivery_date: date,
        start_time,
        end_time
    ) -> None:

        if start_time >= end_time:
            raise HTTPException(
                status_code=400,
                detail="Delivery slot start time must be before end time"
            )

        requested_start = start_time.strftime("%H:%M")
        requested_end = end_time.strftime("%H:%M")

        slot_exists = any(
            slot["start"] == requested_start
            and slot["end"] == requested_end
            for slot in AVAILABLE_DELIVERY_SLOTS
        )

        if not slot_exists:
            raise HTTPException(
                status_code=400,
                detail="Selected delivery slot is not available"
            )

        now = self.get_current_business_datetime()

        # Only apply time-of-day validation when ordering for today.
        if delivery_date == now.date():

            current_time = now.time()

            if start_time <= current_time:
                raise HTTPException(
                    status_code=400,
                    detail="Selected delivery slot has already started"
                )


delivery_service = DeliveryService()