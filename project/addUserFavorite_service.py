from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class Professional(BaseModel):
    """
    Object type representing a professional, including ID, email, and specialty details.
    """

    id: int
    email: str
    specialty: str


class AddFavoriteResponse(BaseModel):
    """
    Response model for POST /user/favorites. Returns the updated list of favorite professionals.
    """

    favorites: List[Professional]


async def addUserFavorite(professional_id: int) -> AddFavoriteResponse:
    """
    Adds a professional to the user's list of favorites. Requires the professional's ID and returns an updated list of favorites.
    This function assumes there is a current user context (like a logged-in user) whose profile is used to add favorites.

    Args:
        professional_id (int): ID of the professional to be added to the user's list of favorites.

    Returns:
        AddFavoriteResponse: Response model for POST /user/favorites. Returns the updated list of favorite professionals.
    """
    current_user_id = 1
    current_profile = await prisma.models.Profile.prisma().find_first(
        where={"userId": current_user_id}, include={"favorites": True}
    )
    if not current_profile:
        raise ValueError("Profile not found for the current user.")
    if current_profile.favorites is None:
        current_profile.favorites = []
    if any((pro.id == professional_id for pro in current_profile.favorites)):
        return AddFavoriteResponse(favorites=current_profile.favorites)
    professional_to_add = await prisma.models.Professional.prisma().find_unique(
        where={"id": professional_id}
    )
    if not professional_to_add:
        raise ValueError("Professional with the provided ID does not exist.")
    await prisma.models.Profile.prisma().update(
        where={"id": current_profile.id},
        data={"favorites": {"connect": [{"id": professional_id}]}},
    )
    updated_profile = await prisma.models.Profile.prisma().find_first(
        where={"id": current_profile.id}, include={"favorites": True}
    )
    if updated_profile is None:
        raise ValueError("Updated profile could not be fetched.")
    return AddFavoriteResponse(favorites=updated_profile.favorites)
