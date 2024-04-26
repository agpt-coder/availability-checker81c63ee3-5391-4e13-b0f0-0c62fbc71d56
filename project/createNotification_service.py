from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class NotificationCreationResponse(BaseModel):
    """
    Response model returning details of the successfully created notification.
    """

    success: bool
    notificationId: int
    message: str


async def createNotification(
    notificationType: str, recipientIds: List[int], messageContent: str
) -> NotificationCreationResponse:
    """
    Creates a new notification. This route is triggered by changes in the Schedule Management system, such as booking confirmations, changes, or cancellations. It requires details like the type of notification, recipient IDs, and message content. This route uses internal logic to determine how and when to send the notification, ensuring users receive updates in real time.

    Args:
        notificationType (str): Type of the notification, e.g., 'CONFIRMATION', 'CHANGE', 'CANCELLATION'.
        recipientIds (List[int]): List of recipient user IDs that will receive this notification.
        messageContent (str): The message content of the notification.

    Returns:
        NotificationCreationResponse: Response model returning details of the successfully created notification.

    Example:
        result = await createNotification('CONFIRMATION', [1, 2, 3], 'Your appointment is confirmed!')
        # Example output:
        # result == NotificationCreationResponse(success=True, notificationId=101, message="Notification created successfully.")
    """
    created_notifications = []
    for user_id in recipientIds:
        notification = await prisma.models.Notification.prisma().create(
            data={"userId": user_id, "message": f"{notificationType}: {messageContent}"}
        )
        created_notifications.append(notification)
    if created_notifications:
        return NotificationCreationResponse(
            success=True,
            notificationId=created_notifications[0].id,
            message="Notifications created successfully.",
        )
    else:
        return NotificationCreationResponse(
            success=False, notificationId=0, message="Failed to create notifications."
        )
