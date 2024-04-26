from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class Notification(BaseModel):
    """
    Model representing the system notifications related to user and administrative events.
    """

    id: int
    userId: int
    message: str
    createdAt: datetime
    read: bool


class UpdateScheduleResponse(BaseModel):
    """
    Confirms the successful update of the schedule with revised details. It also includes any notification details sent as a result of the update.
    """

    updated: bool
    scheduleId: int
    notification: Notification


async def updateSchedule(
    scheduleId: int,
    startTime: datetime,
    endTime: datetime,
    professionalId: int,
    activity: str,
) -> UpdateScheduleResponse:
    """
    Updates an existing schedule entry identified by the schedule ID. It modifies details such as the time slot, the associated activity, or the professional linked with the schedule. Notifications are sent to relevant stakeholders about the schedule change.

    Args:
        scheduleId (int): Unique identifier for the schedule that needs updating.
        startTime (datetime): Updated start time for the schedule.
        endTime (datetime): Updated end time for the schedule.
        professionalId (int): Professional identifier if the schedule is reassigned.
        activity (str): Description of the activity in this schedule.

    Returns:
        UpdateScheduleResponse: Confirms the successful update with details and associated notification.

    Example:
        await updateSchedule(1, datetime(2023, 9, 29, 15), datetime(2023, 9, 29, 17), 2, "Check-up")
        > UpdateScheduleResponse(updated=True, scheduleId=1, notification=Notification(...))
    """
    slot = await prisma.models.Slot.prisma().update(
        where={"id": scheduleId},
        data={
            "startTime": startTime,
            "endTime": endTime,
            "professionalId": professionalId,
        },
    )
    if slot:
        user_notified = await prisma.models.Notification.prisma().create(
            data={
                "userId": professionalId,
                "message": f"Schedule updated: {activity} from {startTime} to {endTime}.",
                "createdAt": datetime.now(),
                "read": False,
            }
        )
        response = UpdateScheduleResponse(
            updated=True,
            scheduleId=scheduleId,
            notification=Notification(
                id=user_notified.id,
                userId=user_notified.userId,
                message=user_notified.message,
                createdAt=user_notified.createdAt,
                read=user_notified.read,
            ),
        )
        return response
    return UpdateScheduleResponse(
        updated=False,
        scheduleId=scheduleId,
        notification=Notification(
            id=0, userId=0, message="", createdAt=datetime.now(), read=False
        ),
    )
