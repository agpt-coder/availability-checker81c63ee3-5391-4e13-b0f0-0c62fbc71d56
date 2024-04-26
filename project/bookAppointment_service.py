from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class BookingResponse(BaseModel):
    """
    Response model for the booking process. It provides details on the success or failure of the booking and, in case of success, the booking details.
    """

    bookingId: Optional[int] = None
    status: str
    message: str


async def bookAppointment(
    userId: int, professionalId: int, slotId: int
) -> BookingResponse:
    """
    Books an appointment slot for a user with a specified professional.

    Args:
        userId (int): The ID of the user who is making the booking.
        professionalId (int): The ID of the professional whose slot is being booked.
        slotId (int): The ID of the slot that is being attempted to book.

    Returns:
        BookingResponse: Response object indicating the outcome of the booking attempt.

    Processes:
        - Checks if the requested slot is valid, active, and available.
        - If available, a booking record is created with a 'PENDING' status.
        - Notifications are sent to both the user and the professional about the booking status.
    """
    slot = await prisma.models.Slot.prisma().find_unique(
        where={"id": slotId}, include={"bookings": True, "professional": True}
    )
    if not slot or not slot.isActive or slot.professional.id != professionalId:
        return BookingResponse(
            status="failed",
            message="Slot is not valid, not active, or does not belong to the specified professional.",
        )
    if slot.bookings and any(
        (booking.status == "CONFIRMED" for booking in slot.bookings)
    ):
        return BookingResponse(
            status="failed", message="Slot is already confirmed for another booking."
        )
    booking = await prisma.models.Booking.prisma().create(
        data={"userId": userId, "slotId": slotId, "status": "PENDING"}
    )
    return BookingResponse(
        bookingId=booking.id,
        status="pending",
        message="Booking is pending and awaiting confirmation.",
    )
