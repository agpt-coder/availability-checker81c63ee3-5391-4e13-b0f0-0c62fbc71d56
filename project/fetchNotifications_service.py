from datetime import datetime
from typing import List, Optional

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


class GetNotificationsResponse(BaseModel):
    """
    This model represents the list of notifications that match the query filters provided by the user.
    """

    notifications: List[Notification]


async def fetchNotifications(
    user_id: int,
    status: Optional[str],
    type: Optional[str],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
) -> GetNotificationsResponse:
    """
    Retrieves a list of notifications for a user. Users can query their notifications based on status (read/unread), type, or date. This route helps users stay informed by allowing them to review past notifications and updates.

    Args:
        user_id (int): The ID of the user whose notifications are being retrieved.
        status (Optional[str]): Filter for the read status of notifications (read or unread).
        type (Optional[str]): Filter for the type of notification.
        start_date (Optional[datetime]): The start date for filtering notifications by date.
        end_date (Optional[datetime]): The end date for filtering notifications by date.

    Returns:
        GetNotificationsResponse: This model represents the list of notifications that match the query filters provided by the user.
    """
    query = prisma.models.Notification.prisma().find_many(
        where={
            "userId": user_id,
            "AND": [
                {"read": {"equals": True}} if status == "read" else {},
                {"read": {"equals": False}} if status == "unread" else {},
                {"createdAt": {"gte": start_date}} if start_date else {},
                {"createdAt": {"lte": end_date}} if end_date else {},
            ],
        }
    )
    notifications = await query
    notification_models = [
        Notification(
            id=n.id,
            userId=n.userId,
            message=n.message,
            createdAt=n.createdAt,
            read=n.read,
        )
        for n in notifications
    ]
    return GetNotificationsResponse(notifications=notification_models)
