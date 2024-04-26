from datetime import datetime
from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class AvailabilityResponse(BaseModel):
    """
    This model describes the availability state of a professional, indicating if they are currently available, busy, or unavailable.
    """

    availability: str


async def checkAvailability(
    professionalId: Optional[int],
    startDate: Optional[datetime],
    endDate: Optional[datetime],
    specialty: Optional[str],
) -> AvailabilityResponse:
    """
    Fetches real-time availability of professionals based on their ID, ability, and specialty. The availability is
    assessed by examining their scheduled and active slots within an optional date range, ensuring the provided querying
    parameters (if any) match their respective scheduling data.

    Args:
        professionalId (Optional[int]): Optional path parameter. The unique identifier of the professional to fetch the availability for.
        startDate (Optional[datetime]): Optional query parameter to filter available slots starting from this date.
        endDate (Optional[datetime]): Optional query parameter to filter available slots up to this date.
        specialty (Optional[str]): Optional query parameter to filter availability by professional specialty.

    Returns:
        AvailabilityResponse: This model describes the availability state of a professional, including if they are
        currently available, busy, or unavailable.

    Example:
        checkAvailability(professionalId=123, startDate=datetime(2023, 1, 1), endDate=datetime(2023, 1, 30), specialty="Dermatology")
        > AvailabilityResponse(availability="available")
    """
    query_conditions = {"isActive": True}
    if professionalId:
        query_conditions["professionalId"] = professionalId
    if specialty:
        query_conditions["professional__specialty"] = specialty
    if startDate:
        query_conditions["startTime__gte"] = startDate
    if endDate:
        query_conditions["endTime__lte"] = endDate
    slots = await prisma.models.Slot.prisma().find_many(
        where=query_conditions, include={"bookings": True, "professional": True}
    )
    availability_status = "unavailable"
    for slot in slots:
        if not slot.bookings or all((b.status == "CANCELLED" for b in slot.bookings)):
            availability_status = "available"
            break
    else:
        if any((slot.bookings for slot in slots)):
            availability_status = "busy"
    return AvailabilityResponse(availability=availability_status)
