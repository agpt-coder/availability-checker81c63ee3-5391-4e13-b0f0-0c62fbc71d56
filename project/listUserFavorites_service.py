from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class ProfessionalInfo(BaseModel):
    """
    Basic contact information of a professional.
    """

    professional_id: int
    email: str
    specialty: str


class FavoritesResponse(BaseModel):
    """
    Response model returning a list of favorite professionals with basic contact information.
    """

    favorites: List[ProfessionalInfo]


async def listUserFavorites(user_id: int) -> FavoritesResponse:
    """
    Lists all favorite professionals of the user, pulled from their profile. Includes professional IDs and basic contact info. Useful for quickly accessing preferred professionals.

    Args:
        user_id (int): The unique identifier of the user for whom to retrieve favorite professionals.

    Returns:
        FavoritesResponse: Response model returning a list of favorite professionals with basic contact information.

    Example:
        user_favorites = await listUserFavorites(1)
        > FavoritesResponse(favorites=[ProfessionalInfo(professional_id=5, email='prof5@example.com', specialty='Dermatology')])
    """
    profiles = await prisma.models.Profile.prisma().find_many(
        where={"userId": user_id}, include={"favorites": True}
    )
    favorites_list = []
    for profile in profiles:
        if profile.favorites:
            for favorite in profile.favorites:
                favorite_info = ProfessionalInfo(
                    professional_id=favorite.id,
                    email=favorite.email,
                    specialty=favorite.specialty,
                )
                favorites_list.append(favorite_info)
    return FavoritesResponse(favorites=favorites_list)
