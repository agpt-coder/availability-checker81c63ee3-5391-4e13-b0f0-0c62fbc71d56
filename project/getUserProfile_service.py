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


async def getUserProfile(user_id: int) -> UserProfileResponse:
    """
    Retrieves the user profile data including booked appointments and favorite professionals. It integrates with the Schedule Management to pull the latest booking details. Response includes user ID, name, email, booked appointments, and favorites list.

    Args:
        user_id (int): The unique identifier of the user whose profile details are being retrieved.

    Returns:
        UserProfileResponse: Provides detailed user profile information including both personal details and professional affiliations like booked appointments and favorite professionals.
    """
    user = await prisma.models.User.prisma().find_unique(
        where={"id": user_id},
        include={
            "profiles": {"include": {"favorites": True}},
            "bookings": {"include": {"slot": {"include": {"professional": True}}}},
        },
    )
    if user is None or not user.profiles:
        raise ValueError("User or user profile not found!")
    profile = user.profiles[0]
    if user.bookings:
        bookings = [
            BookingOverview(
                booking_id=booking.id,
                datetime=booking.slot.startTime,
                status=booking.status,
                professional_name=booking.slot.professional.email,
            )
            for booking in user.bookings
            if booking.slot and booking.slot.professional
        ]
    else:
        bookings = []
    if profile.favorites:
        favorites = [
            ProfessionalMini(
                professional_id=prof.id, name=prof.email, specialty=prof.specialty
            )
            for prof in profile.favorites
        ]
    else:
        favorites = []
    fullname = f"{profile.firstName} {profile.lastName}"
    return UserProfileResponse(
        user_id=user.id,
        name=fullname,
        email=user.email,
        booked_appointments=bookings,
        favorites=favorites,
    )
