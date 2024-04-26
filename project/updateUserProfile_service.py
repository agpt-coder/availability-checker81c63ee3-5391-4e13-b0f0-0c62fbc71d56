from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class UserProfileUpdateResponse(BaseModel):
    """
    This model returns the updated details of the user's profile to confirm changes have been stored.
    """

    userId: int
    email: str
    favorites: List[int]


async def updateUserProfile(
    userId: int, email: str, favorites: List[int]
) -> UserProfileUpdateResponse:
    """
    Updates user-specific information such as email or favorite professionals. Requires current user data and the modifications. Returns the updated user profile.

    Args:
    userId (int): The unique identifier of the user to be updated.
    email (str): The new or updated email address of the user.
    favorites (List[int]): List of IDs of the professionals marked as favorite by the user.

    Returns:
    UserProfileUpdateResponse: This model returns the updated details of the user's profile to confirm changes have been stored.
    """
    await prisma.models.User.prisma().update(
        where={"id": userId}, data={"email": email}
    )
    profile = await prisma.models.Profile.prisma().find_unique(where={"userId": userId})
    if not profile:
        raise ValueError("Profile not found for the given user ID.")
    await prisma.models.Profile.prisma().update(
        where={"id": profile.id}, data={"favorites": {"set": []}}
    )
    for favorite_id in favorites:
        await prisma.models.Profile.prisma().update(
            where={"id": profile.id},
            data={"favorites": {"connect": {"id": favorite_id}}},
        )
    return UserProfileUpdateResponse(userId=userId, email=email, favorites=favorites)
