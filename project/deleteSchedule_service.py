from datetime import datetime
from enum import Enum

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class DeleteScheduleResponse(BaseModel):
    """
    Communicates the result of the schedule deletion operation. Includes message of operation's success or failure.
    """

    success: bool
    message: str


class Role(Enum):
    ADMIN: str = "ADMIN"
    PROFESSIONAL: str = "PROFESSIONAL"
    REGISTERED_USER: str = "REGISTERED_USER"
    GUEST: str = "GUEST"


async def deleteSchedule(
    scheduleId: int, requesterRole: Role
) -> DeleteScheduleResponse:
    """
    Removes a schedule entry from the system using the schedule ID. This operation must ensure that it cleans up all associated data
    and releases any booked resources or slots. Notifications are sent to affected parties to advise them of the cancellation.

    Args:
        scheduleId (int): The identifier for the schedule to be removed.
        requesterRole (Role): The role of the person making the request. Must be either Admin or Professional.

    Returns:
        DeleteScheduleResponse: Communicates the result of the schedule deletion operation. Includes message of operation's success or failure.
    """
    if requesterRole not in [Role.ADMIN, Role.PROFESSIONAL]:
        return DeleteScheduleResponse(
            success=False, message="Request denied: unauthorized role."
        )
    slot = await prisma.models.Slot.prisma().find_unique(where={"id": scheduleId})
    if not slot:
        return DeleteScheduleResponse(success=False, message="No such schedule exists.")
    bookings = await prisma.models.Booking.prisma().find_many(
        where={"slotId": scheduleId}
    )
    for booking in bookings:
        await prisma.models.Booking.prisma().update(
            where={"id": booking.id},
            data={"status": prisma.enums.BookingStatus.CANCELLED},
        )
        await prisma.models.Notification.prisma().create(
            data={
                "userId": booking.userId,
                "message": f"Booking for slot starting at {slot.startTime} has been cancelled.",
                "createdAt": datetime.now(),
                "read": False,
            }
        )
    await prisma.models.Slot.prisma().update(
        where={"id": scheduleId}, data={"isActive": False}
    )
    return DeleteScheduleResponse(
        success=True, message="Schedule successfully deleted."
    )
