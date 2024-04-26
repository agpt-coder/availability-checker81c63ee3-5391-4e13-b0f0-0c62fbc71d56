import prisma
import prisma.models
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel


class LoginResponse(BaseModel):
    """
    Produces a JWT token for session management if the credentials are verified correctly.
    """

    token: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict) -> str:
    """
    Generates a JWT access token.

    Args:
        data (dict): The payload to encode into the JWT token.

    Returns:
        str: The JWT access token.
    """
    SECRET_KEY = "your_secret_key"
    ALGORITHM = "HS256"
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def login(username: str, password: str) -> LoginResponse:
    """
    Authenticates a user, allowing them to log in to the system. It accepts credentials, such as username and password, verifies them against the stored data, and returns a JWT token for session management if the credentials are correct.

    Args:
        username (str): The username of the user trying to login. This can be an email or a user-registered name.
        password (str): The password for the given username, used for authentication purposes.

    Returns:
        LoginResponse: Produces a JWT token for session management if the credentials are verified correctly.
    """
    user = await prisma.models.User.prisma().find_unique(where={"email": username})
    if user and pwd_context.verify(password, user.password):
        token_data = {"sub": user.email, "uid": str(user.id)}
        token = create_access_token(token_data)
        return LoginResponse(token=token)
    raise Exception("Invalid credentials")
