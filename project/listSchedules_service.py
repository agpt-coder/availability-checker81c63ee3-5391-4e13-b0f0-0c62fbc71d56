from datetime import datetime
from typing import List

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class ProfessionalSchedule(BaseModel):
    """
    Detailed information of each schedule slot including slot timings, associated bookings and booking status.
    """

    slotId: int
    startTime: datetime
    endTime: datetime
    isActive: bool
    bookingStatus: prisma.enums.BookingStatus


class ScheduleResponse(BaseModel):
    """
    Response model containing lists of schedules, each detailing the slots booked, timings, and booking status for a professional.
    """

    schedules: List[ProfessionalSchedule]


async def listSchedules(professionalId: int) -> ScheduleResponse:
    """
    Lists all schedule entries for a specific professional by their ID. This is useful for professionals or admins to get a comprehensive view of all booked activities and times. It helps in planning and verifying availability for new bookings.

    Args:
    professionalId (int): The unique identifier of the professional whose schedule is to be fetched.

    Returns:
    ScheduleResponse: Response model containing lists of schedules, each detailing the slots booked, timings, and booking status for a professional.
    """
    slots_result = await prisma.models.Slot.prisma().find_many(
        where={"professionalId": professionalId}, include={"bookings": True}
    )
    schedules = []
    for slot in slots_result:
        if slot.bookings:
            latest_booking = max(slot.bookings, key=lambda b: b.createdAt)
            booking_status = latest_booking.status
        else:
            booking_status = prisma.enums.BookingStatus.PENDING
        professional_schedule = ProfessionalSchedule(
            slotId=slot.id,
            startTime=slot.startTime,
            endTime=slot.endTime,
            isActive=slot.isActive,
            bookingStatus=booking_status,
        )
        schedules.append(professional_schedule)
    return ScheduleResponse(schedules=schedules)
