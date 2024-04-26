from datetime import datetime
from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class FetchAvailabilityRequest(BaseModel):
    """
    Request model for fetching real-time availability data of professionals. As there are no specific request parameters required, this model is kept empty to signify it can handle generic queries for availability.
    """

    pass


class SlotDetails(BaseModel):
    """
    Detail of each availability slot including timing and booking status.
    """

    startTime: datetime
    endTime: datetime
    isActive: bool
    bookings: int


class ProfessionalAvailability(BaseModel):
    """
    Stores individual professional's availability data including detailed slots and booking statuses.
    """

    professionalId: int
    fullName: str
    specialty: str
    slots: List[SlotDetails]


class FetchAvailabilityResponse(BaseModel):
    """
    Response model that provides a list of professionals along with associated availability details. The response includes dynamic updates from the Schedule Management module.
    """

    professionals: List[ProfessionalAvailability]


async def getAvailability(
    request: FetchAvailabilityRequest,
) -> FetchAvailabilityResponse:
    """
    Fetches real-time availability data of professionals. This endpoint queries the Schedule Management module to retrieve current activity or scheduled data. It is expected to return a list of professionals along with their current availability status. The response is dynamically updated as the Schedule Management data changes.

    Args:
        request (FetchAvailabilityRequest): Request model for fetching real-time availability data of professionals. As there are no specific request parameters required, this model is kept empty to signify it can handle generic queries for availability.

    Returns:
        FetchAvailabilityResponse: Response model that provides a list of professionals along with associated availability details. The response includes dynamic updates from the Schedule Management module.
    """
    professionals_data = await prisma.models.Professional.prisma().find_many(
        include={
            "availableSlots": {
                "where": {"isActive": True},
                "include": {"bookings": True},
            }
        }
    )
    professionals: List[ProfessionalAvailability] = [
        ProfessionalAvailability(
            professionalId=prof.id,
            fullName=f"{prof.favoritesBy[0].firstName} {prof.favoritesBy[0].lastName}"
            if prof.favoritesBy
            else "Name Unknown",
            specialty=prof.specialty,
            slots=[
                SlotDetails(
                    startTime=slot.startTime,
                    endTime=slot.endTime,
                    isActive=slot.isActive,
                    bookings=len(slot.bookings),
                )
                for slot in prof.availableSlots
            ],
        )
        for prof in professionals_data
        if prof.availableSlots
    ]
    return FetchAvailabilityResponse(professionals=professionals)
