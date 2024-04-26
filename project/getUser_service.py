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


async def getUser(userId: int) -> UserProfileResponse:
    """
    Retrieves details of a specific user by their unique identifier (userId). This is used to allow a user or admin to view user profiles. If the
    user is looking up their own profile, it returns the full profile; if an admin is viewing, it includes additional administrative fields.

    Args:
        userId (int): The unique identifier for the user whose profile is to be retrieved.

    Returns:
        UserProfileResponse: Provides detailed user profile information including both personal details and professional affiliations like booked
        appointments and favorite professionals.
    """
    user = await prisma.models.User.prisma().find_unique(
        where={"id": userId},
        include={
            "profiles": True,
            "bookings": {"include": {"slot": {"include": {"professional": True}}}},
        },
    )
    if user is None:
        raise ValueError("User not found")
    profile = user.profiles[0] if user.profiles else None
    if profile is None:
        raise ValueError("User profile not found")
    full_name = f"{profile.firstName} {profile.lastName}"
    booked_appointments = [
        BookingOverview(
            booking_id=booking.id,
            datetime=booking.slot.startTime,
            status=booking.status,
            professional_name=booking.slot.professional.email,
        )
        for booking in user.bookings
        if booking.slot and booking.slot.professional
    ]
    favorites = [
        ProfessionalMini(
            professional_id=prof.id, name=prof.email, specialty=prof.specialty
        )
        for prof in profile.favorites
    ]
    return UserProfileResponse(
        user_id=user.id,
        name=full_name,
        email=user.email,
        booked_appointments=booked_appointments,
        favorites=favorites,
    )
