from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class FetchAvailabilityRequest(BaseModel):
    """
    Request model for fetching real-time availability data of professionals. As there are no specific request parameters required, this model is kept empty to signify it can handle generic queries for availability.
    """

    pass


class AvailabilityResponse(BaseModel):
    """
    This model describes the availability state of a professional, indicating if they are currently available, busy, or unavailable.
    """

    availability: str


async def getProfessionalAvailability(
    request: FetchAvailabilityRequest,
) -> AvailabilityResponse:
    """
    Retrieves real-time availability for a specific professional by their unique ID. This function connects to the Schedule Management module to pull detailed availability status for the requested professional. Ideal for users needing detailed, individual data.

    Args:
        request (FetchAvailabilityRequest): Request model for fetching real-time availability data of professionals, including the professional's unique ID.

    Returns:
        AvailabilityResponse: This model describes the availability state of a professional, indicating if they are currently available, busy, or unavailable based on existing bookings and active slots.
    """
    current_time = datetime.now()
    upcoming_and_current_slots = await prisma.models.Slot.prisma().find_many(
        where={
            "professionalId": request.professional_id,
            "isActive": True,
            "OR": [
                {"startTime": {"lte": current_time}},
                {"endTime": {"gt": current_time}},
            ],
        },
        include={"bookings": {"where": {"status": "CONFIRMED"}}},
    )  # TODO(autogpt): Cannot access member "professional_id" for type "FetchAvailabilityRequest"
    #     Member "professional_id" is unknown. reportAttributeAccessIssue
    currently_available = all(
        (
            not slot.bookings
            for slot in upcoming_and_current_slots
            if slot.startTime <= current_time < slot.endTime
        )
    )
    availability_status = "available" if currently_available else "busy"
    return AvailabilityResponse(availability=availability_status)
