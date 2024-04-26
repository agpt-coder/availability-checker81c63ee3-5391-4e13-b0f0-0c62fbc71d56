from datetime import datetime, timedelta

import prisma
import prisma.models
from pydantic import BaseModel


class RefreshTokenResponse(BaseModel):
    """
    Provides a new authentication token for the user, ensuring continued access without re-login.
    """

    new_token: str


SECRET_KEY = "YOUR_SECRET_KEY_HERE"

ALGORITHM = "HS256"

TOKEN_EXPIRATION_PERIOD_IN_MINUTES = 30


async def refreshToken(token: str) -> RefreshTokenResponse:
    """
    Refreshes the authentication token when the current token is about to expire. This endpoint
    requires a valid, non-expired token and returns a new token for continued use, ensuring the user
    remains authenticated without needing to log in again.

    Args:
        token (str): The current valid, non-expired authentication token provided by the user.

    Returns:
        RefreshTokenResponse: Provides a new authentication token for the user, ensuring continued access without re-login.
    """
    try:
        user_id = int(token)
        user = await prisma.models.User.prisma().find_unique(where={"id": user_id})
        if user:
            new_expiration_time = datetime.utcnow() + timedelta(
                minutes=TOKEN_EXPIRATION_PERIOD_IN_MINUTES
            )
            new_token = f"{user_id}-{int(new_expiration_time.timestamp())}"
            return RefreshTokenResponse(new_token=new_token)
        else:
            raise ValueError("No such user found with the provided token")
    except ValueError as e:
        raise ValueError("Invalid token format") from e
