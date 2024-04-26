from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class CreateScheduleResponse(BaseModel):
    """
    Response model indicating the successful creation of a schedule. Includes details of the created schedule and initial status.
    """

    scheduleId: int
    professionalId: int
    wasNotificationSent: bool
    isActive: bool


async def createSchedule(
    professionalId: int,
    startTime: datetime,
    endTime: datetime,
    activityType: str,
    isActive: bool,
) -> CreateScheduleResponse:
    """
    Enables the creation of a new schedule entry for a professional. It accepts details such as time slots, professional ID, and activity type. This endpoint requires proper validations to avoid conflicts in the scheduling logic. Upon successful creation, it triggers an interaction with the Notification Engine to alert the professional of a new schedule entry.

    Args:
        professionalId (int): Unique identifier for the professional for whom the schedule is being created.
        startTime (datetime): Starting time of the new schedule slot.
        endTime (datetime): Ending time of the new schedule slot.
        activityType (str): Type of activity or session planned for this time slot.
        isActive (bool): Flag to activate or deactivate the slot immediately upon creation.

    Returns:
        CreateScheduleResponse: Response model indicating the successful creation of a schedule. Includes details of the created schedule and initial status.
    """
    professional = await prisma.models.Professional.prisma().find_unique(
        where={"id": professionalId}
    )
    if not professional:
        raise ValueError("Professional with the given ID does not exist")
    existing_slots = await prisma.models.Slot.prisma().find_many(
        where={
            "professionalId": professionalId,
            "startTime": {"lte": endTime},
            "endTime": {"gte": startTime},
        }
    )
    if existing_slots:
        raise ValueError("This time slot conflicts with an existing schedule.")
    new_slot = await prisma.models.Slot.prisma().create(
        data={
            "startTime": startTime,
            "endTime": endTime,
            "professionalId": professionalId,
            "isActive": isActive,
        }
    )
    notification_message = f"New schedule created from {startTime} to {endTime}."
    notification = await prisma.models.Notification.prisma().create(
        data={"userId": professionalId, "message": notification_message, "read": False}
    )
    was_notification_sent = notification.id is not None
    return CreateScheduleResponse(
        scheduleId=new_slot.id,
        professionalId=professionalId,
        wasNotificationSent=was_notification_sent,
        isActive=new_slot.isActive,
    )
