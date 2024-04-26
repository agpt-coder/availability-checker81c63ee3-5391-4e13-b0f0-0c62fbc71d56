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


class RemoveFavoriteResponse(BaseModel):
    """
    Response model confirming the deletion and providing an updated list of favorites post-modification.
    """

    favorites: List[Professional]


async def removeUserFavorite(professionalId: int) -> RemoveFavoriteResponse:
    """
    Removes a professional from the user's list of favorites. Needs the professional's ID for removal. Confirms the removal with an updated list of favorites.

    Args:
        professionalId (int): The unique identifier of the professional to be removed from the user's favorite list.

    Returns:
        RemoveFavoriteResponse: Response model confirming the deletion and providing an updated list of favorites post-modification.
    """
    profile = await prisma.models.Profile.prisma().find_first(
        where={"favorites": {"some": {"id": professionalId}}},
        include={"favorites": True},
    )
    if not profile:
        return RemoveFavoriteResponse(favorites=[])
    await prisma.models.Profile.prisma().update(
        where={"id": profile.id},
        data={"favorites": {"disconnect": [{"id": professionalId}]}},
    )
    updated_profile = await prisma.models.Profile.prisma().find_unique(
        where={"id": profile.id}, include={"favorites": True}
    )
    updated_favorites = (
        [
            Professional(id=prof.id, email=prof.email, specialty=prof.specialty)
            for prof in updated_profile.favorites
        ]
        if updated_profile and updated_profile.favorites
        else []
    )
    return RemoveFavoriteResponse(favorites=updated_favorites)
