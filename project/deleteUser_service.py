import prisma
import prisma.models
from pydantic import BaseModel


class DeleteUserResponseModel(BaseModel):
    """
    Response model for the delete user operation. It indicates whether the deletion was successful and provides an appropriate message.
    """

    success: bool
    message: str


async def deleteUser(userId: int) -> DeleteUserResponseModel:
    """
    Deletes a user account by their userId. This asynchronous function checks if the user exists and then deletes the user
    from the database. The function returns a response model indicating the success of the operation and an appropriate message.

    Args:
        userId (int): The unique identifier of the user to be deleted.

    Returns:
        DeleteUserResponseModel: Response model for the delete user operation. It indicates whether the deletion was successful and provides an appropriate message.

    Example:
        response = await deleteUser(1)
        > DeleteUserResponseModel(success=True, message="User with ID 1 has been successfully deleted.")
    """
    user = await prisma.models.User.prisma().find_unique(where={"id": userId})
    if not user:
        return DeleteUserResponseModel(
            success=False, message=f"No user found with ID {userId}."
        )
    try:
        await prisma.models.User.prisma().delete(where={"id": userId})
        return DeleteUserResponseModel(
            success=True,
            message=f"User with ID {userId} has been successfully deleted.",
        )
    except Exception as e:
        return DeleteUserResponseModel(success=False, message=str(e))
