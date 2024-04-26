import prisma
import prisma.models
from pydantic import BaseModel


class UpdateNotificationStatusResponse(BaseModel):
    """
    Response model confirming the updated status of the notification. It returns the id and new read status ensuring that the client is aware of the successful update.
    """

    id: int
    read: bool


class Role:
    """
    Enum representing different roles within the system.
    """

    ADMIN: str = "ADMIN"
    PROFESSIONAL: str = "PROFESSIONAL"
    REGISTERED_USER: str = "REGISTERED_USER"
    GUEST: str = "GUEST"


async def updateNotificationStatus(
    id: int, read: bool, updater_role: Role
) -> UpdateNotificationStatusResponse:
    """
    Updates the status of a specific notification, typically from 'unread' to 'read'.

    Args:
        id (int): The unique identifier of the notification to be updated.
        read (bool): The updated status of the notification, indicating whether it has been read by the user.
        updater_role (Role): Role of the user updating the notification, to ensure that only allowed roles (Admin, Professional, Registered User) can change the notification status.

    Returns:
        UpdateNotificationStatusResponse: Response model confirming the updated status of the notification. It returns the id and new read status ensuring that the client is aware of the successful update.

    Raises:
        ValueError: If the `updater_role` is not permitted to update notification status.
        Exception: For any database related errors or if the notification ID does not exist.
    """
    if updater_role not in [Role.ADMIN, Role.PROFESSIONAL, Role.REGISTERED_USER]:
        raise ValueError(
            "The updater role does not have permission to update the notification status"
        )
    notification = await prisma.models.Notification.prisma().find_unique(
        where={"id": id}
    )
    if not notification:
        raise Exception("Notification with the provided ID does not exist")
    updated_notification = await prisma.models.Notification.prisma().update(
        where={"id": id}, data={"read": read}
    )
    return UpdateNotificationStatusResponse(
        id=updated_notification.id, read=updated_notification.read
    )
