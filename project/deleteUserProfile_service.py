import prisma
import prisma.models
from pydantic import BaseModel


class DeleteUserProfileResponse(BaseModel):
    """
    Provides a confirmation message indicating that the user profile and all related data have been successfully deleted.
    """

    message: str


async def deleteUserProfile(userId: int) -> DeleteUserProfileResponse:
    """
    Deletes a user profile, removing all associated data including booked appointments and favorites. Confirms the deletion with a success message.

    Args:
        userId (int): The unique identifier of the user whose profile is to be deleted.

    Returns:
        DeleteUserProfileResponse: Provides a confirmation message indicating that the user profile and all related data have been successfully deleted.

    Example:
        response = deleteUserProfile(1)
        response.message
        > 'User and all related data have been successfully deleted.'
    """
    await prisma.models.Booking.prisma().delete_many(where={"userId": userId})
    await prisma.models.Notification.prisma().delete_many(where={"userId": userId})
    profiles = await prisma.models.Profile.prisma().find_many(where={"userId": userId})
    for profile in profiles:
        await prisma.models.Profile.prisma().update(
            where={"id": profile.id}, data={"favorites": {"set": []}}
        )
    await prisma.models.Profile.prisma().delete_many(where={"userId": userId})
    await prisma.models.User.prisma().delete(where={"id": userId})
    return DeleteUserProfileResponse(
        message="User and all related data have been successfully deleted."
    )
