from datetime import datetime
from typing import List

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class BookingOverview(BaseModel):
    """
    Summarized details for a booked appointment.
    """

    booking_id: int
    datetime: datetime
    status: prisma.enums.BookingStatus
    professional_name: str


class ProfessionalMini(BaseModel):
    """
    Reduced detail of a Professional entity, for favorites listing.
    """

    professional_id: int
    name: str
    specialty: str


class UserProfileResponse(BaseModel):
    """
    Provides detailed user profile information including both personal details and professional affiliations like booked appointments and favorite professionals.
    """

    user_id: int
    name: str
    email: str
    booked_appointments: List[BookingOverview]
    favorites: List[ProfessionalMini]


async def createUserProfile(
    userId: int, firstName: str, lastName: str, email: str
) -> UserProfileResponse:
    """
    Creates a new user profile with initial details such as user ID, name, and email. Response confirms the creation with the user profile data.

    Args:
        userId (int): Unique identifier of the user for whom the profile is being created.
        firstName (str): First name of the user.
        lastName (str): Last name of the user.
        email (str): Email address of the user; must be unique across all profiles.

    Returns:
        UserProfileResponse: Provides detailed user profile information including both personal details and professional affiliations like booked appointments and favorite professionals.

    Example:
        response = await createUserProfile(1, 'Jane', 'Doe', 'jane.doe@example.com')
        print(response)
    """
    user = await prisma.models.User.prisma().create(
        data={
            "id": userId,
            "email": email,
            "password": "DefaultPassword",
            "role": "REGISTERED_USER",
            "profiles": {
                "create": {
                    "firstName": firstName,
                    "lastName": lastName,
                    "userId": userId,
                }
            },
        }
    )
    profile = await prisma.models.Profile.prisma().find_unique(where={"userId": userId})
    if not profile:
        raise ValueError("Profile creation failed")
    bookings = await prisma.models.Booking.prisma().find_many(
        where={"userId": userId}, include={"slot": {"professional": True}}
    )
    booked_appointments = [
        BookingOverview(
            booking_id=b.id,
            datetime=b.slot.startTime if b.slot else None,
            status=b.status,
            professional_name=b.slot.professional.email
            if b.slot and b.slot.professional
            else "Unassigned",
        )
        for b in bookings
    ]
    favorites = await prisma.models.Professional.prisma().find_many(
        where={"favoritesBy": {"any": {"userId": userId}}}
    )
    favorite_list = [
        ProfessionalMini(
            professional_id=prof.id, name=prof.email, specialty=prof.specialty
        )
        for prof in favorites
    ]
    user_profile_response = UserProfileResponse(
        user_id=user.id,
        name=f"{firstName} {lastName}",
        email=user.email,
        booked_appointments=booked_appointments,
        favorites=favorite_list,
    )
    return user_profile_response
