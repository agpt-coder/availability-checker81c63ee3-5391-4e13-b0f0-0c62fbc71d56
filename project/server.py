import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

import prisma
import prisma.enums
import project.addUserFavorite_service
import project.apiOptions_service
import project.bookAppointment_service
import project.checkAvailability_service
import project.createNotification_service
import project.createSchedule_service
import project.createUser_service
import project.createUserProfile_service
import project.deleteNotification_service
import project.deleteSchedule_service
import project.deleteUser_service
import project.deleteUserProfile_service
import project.fetchNotifications_service
import project.getAvailability_service
import project.getProfessionalAvailability_service
import project.getUser_service
import project.getUserProfile_service
import project.listSchedules_service
import project.listUserFavorites_service
import project.login_service
import project.refreshToken_service
import project.removeUserFavorite_service
import project.updateNotificationStatus_service
import project.updateSchedule_service
import project.updateUser_service
import project.updateUserProfile_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="Availability Checker",
    lifespan=lifespan,
    description="Function that returns the real-time availability of professionals, updating based on current activity or schedule.",
)


@app.post(
    "/user/profile",
    response_model=project.createUserProfile_service.UserProfileResponse,
)
async def api_post_createUserProfile(
    userId: int, firstName: str, lastName: str, email: str
) -> project.createUserProfile_service.UserProfileResponse | Response:
    """
    Creates a new user profile with initial details such as user ID, name, and email. Response confirms the creation with the user profile data.
    """
    try:
        res = await project.createUserProfile_service.createUserProfile(
            userId, firstName, lastName, email
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/availability",
    response_model=project.checkAvailability_service.AvailabilityResponse,
)
async def api_get_checkAvailability(
    professionalId: Optional[int],
    startDate: Optional[datetime],
    endDate: Optional[datetime],
    specialty: Optional[str],
) -> project.checkAvailability_service.AvailabilityResponse | Response:
    """
    Fetches real-time availability of professionals. It queries the scheduling database to determine available time slots based on professionals’ current activities and schedules. Each query response includes structured data indicating the start and end times of available slots. This endpoint is accessed every time a user wishes to view availability.
    """
    try:
        res = await project.checkAvailability_service.checkAvailability(
            professionalId, startDate, endDate, specialty
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/book", response_model=project.bookAppointment_service.BookingResponse)
async def api_post_bookAppointment(
    userId: int, professionalId: int, slotId: int
) -> project.bookAppointment_service.BookingResponse | Response:
    """
    Accepts user-selected time slots and professional details and sends this info to the Schedule Management System for processing and confirming the booking. This function performs validations to ensure the slot is still available and compatible with the professional’s schedule, using transaction mechanisms to maintain consistency. Expect confirmation of booking or error message in response.
    """
    try:
        res = await project.bookAppointment_service.bookAppointment(
            userId, professionalId, slotId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/notifications",
    response_model=project.createNotification_service.NotificationCreationResponse,
)
async def api_post_createNotification(
    notificationType: str, recipientIds: List[int], messageContent: str
) -> project.createNotification_service.NotificationCreationResponse | Response:
    """
    Creates a new notification. This route is triggered by changes in the Schedule Management system, such as booking confirmations, changes, or cancellations. It requires details like the type of notification, recipient IDs, and message content. This route uses internal logic to determine how and when to send the notification, ensuring users receive updates in real time.
    """
    try:
        res = await project.createNotification_service.createNotification(
            notificationType, recipientIds, messageContent
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/notifications",
    response_model=project.fetchNotifications_service.GetNotificationsResponse,
)
async def api_get_fetchNotifications(
    user_id: int,
    status: Optional[str],
    type: Optional[str],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
) -> project.fetchNotifications_service.GetNotificationsResponse | Response:
    """
    Retrieves a list of notifications for a user. Users can query their notifications based on status (read/unread), type, or date. This route helps users stay informed by allowing them to review past notifications and updates.
    """
    try:
        res = await project.fetchNotifications_service.fetchNotifications(
            user_id, status, type, start_date, end_date
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/users/{userId}", response_model=project.deleteUser_service.DeleteUserResponseModel
)
async def api_delete_deleteUser(
    userId: int,
) -> project.deleteUser_service.DeleteUserResponseModel | Response:
    """
    Deletes a user account by their userId. This endpoint will permit deletion by the account owner or by an admin. It requires authentication and provides confirmation upon successful deletion or details on why deletion was not allowed.
    """
    try:
        res = await project.deleteUser_service.deleteUser(userId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/user/favorites",
    response_model=project.listUserFavorites_service.FavoritesResponse,
)
async def api_get_listUserFavorites(
    user_id: int,
) -> project.listUserFavorites_service.FavoritesResponse | Response:
    """
    Lists all favorite professionals of the user, pulled from their profile. Includes professional IDs and basic contact info. Useful for quickly accessing preferred professionals.
    """
    try:
        res = await project.listUserFavorites_service.listUserFavorites(user_id)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/user/favorites",
    response_model=project.addUserFavorite_service.AddFavoriteResponse,
)
async def api_post_addUserFavorite(
    professional_id: int,
) -> project.addUserFavorite_service.AddFavoriteResponse | Response:
    """
    Adds a professional to the user's list of favorites. Requires the professional's ID. Returns updated list of favorites.
    """
    try:
        res = await project.addUserFavorite_service.addUserFavorite(professional_id)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/auth/login", response_model=project.login_service.LoginResponse)
async def api_post_login(
    username: str, password: str
) -> project.login_service.LoginResponse | Response:
    """
    Authenticates a user, allowing them to log into the system. It accepts credentials, such as username and password, verifies them against the stored data, and returns a JWT token for session management if the credentials are correct.
    """
    try:
        res = await project.login_service.login(username, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/user/profile",
    response_model=project.updateUserProfile_service.UserProfileUpdateResponse,
)
async def api_put_updateUserProfile(
    userId: int, email: str, favorites: List[int]
) -> project.updateUserProfile_service.UserProfileUpdateResponse | Response:
    """
    Updates user-specific information such as email or favorite professionals. Requires current user data and the modifications. Returns the updated user profile.
    """
    try:
        res = await project.updateUserProfile_service.updateUserProfile(
            userId, email, favorites
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/auth/refresh", response_model=project.refreshToken_service.RefreshTokenResponse
)
async def api_post_refreshToken(
    token: str,
) -> project.refreshToken_service.RefreshTokenResponse | Response:
    """
    Refreshes the authentication token when the current token is about to expire. This endpoint requires a valid, non-expired token and returns a new token for continued use, ensuring the user remains authenticated without needing to log in again.
    """
    try:
        res = await project.refreshToken_service.refreshToken(token)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/notifications/{id}",
    response_model=project.deleteNotification_service.DeleteNotificationResponse,
)
async def api_delete_deleteNotification(
    id: int,
) -> project.deleteNotification_service.DeleteNotificationResponse | Response:
    """
    Deletes a specific notification. This route is available for users to manage their notification clutter, removing older or irrelevant notifications from their view.
    """
    try:
        res = await project.deleteNotification_service.deleteNotification(id)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.options(
    "/availability",
    response_model=project.apiOptions_service.CheckAvailabilityOptionsResponse,
)
async def api_options_apiOptions(
    access_control_request_method: str, access_control_request_headers: str
) -> project.apiOptions_service.CheckAvailabilityOptionsResponse | Response:
    """
    Provides details about the supported methods and requirements for the check availability endpoint. It responds with accepted request formats and other API usage policies. This is useful for developer integrations and troubleshooting.
    """
    try:
        res = project.apiOptions_service.apiOptions(
            access_control_request_method, access_control_request_headers
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/user/profile",
    response_model=project.deleteUserProfile_service.DeleteUserProfileResponse,
)
async def api_delete_deleteUserProfile(
    userId: int,
) -> project.deleteUserProfile_service.DeleteUserProfileResponse | Response:
    """
    Deletes a user profile, removing all associated data including booked appointments and favorites. Confirms the deletion with a success message.
    """
    try:
        res = await project.deleteUserProfile_service.deleteUserProfile(userId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/schedules/{professionalId}",
    response_model=project.listSchedules_service.ScheduleResponse,
)
async def api_get_listSchedules(
    professionalId: int,
) -> project.listSchedules_service.ScheduleResponse | Response:
    """
    Lists all schedule entries for a specific professional by their ID. This is useful for professionals or admins to get a comprehensive view of all booked activities and times. It helps in planning and verifying availability for new bookings.
    """
    try:
        res = await project.listSchedules_service.listSchedules(professionalId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.patch(
    "/notifications/{id}",
    response_model=project.updateNotificationStatus_service.UpdateNotificationStatusResponse,
)
async def api_patch_updateNotificationStatus(
    id: int, read: bool, updater_role: prisma.enums.Role
) -> project.updateNotificationStatus_service.UpdateNotificationStatusResponse | Response:
    """
    Updates the status of a specific notification, typically from 'unread' to 'read'. This API is essential for maintaining the relevance and currentness of user interfaces, ensuring that users have an accurate count of new versus reviewed notifications.
    """
    try:
        res = await project.updateNotificationStatus_service.updateNotificationStatus(
            id, read, updater_role
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/schedules/{scheduleId}",
    response_model=project.updateSchedule_service.UpdateScheduleResponse,
)
async def api_put_updateSchedule(
    scheduleId: int,
    startTime: datetime,
    endTime: datetime,
    professionalId: int,
    activity: str,
) -> project.updateSchedule_service.UpdateScheduleResponse | Response:
    """
    Updates an existing schedule entry identified by the schedule ID. It requires complete or partial schedule details for updates such as changing the time slot, modifying the associated activity, or altering the professional linked with the schedule entry. Each update sends a notification via the Notification Engine to inform relevant stakeholders of the schedule change.
    """
    try:
        res = await project.updateSchedule_service.updateSchedule(
            scheduleId, startTime, endTime, professionalId, activity
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/schedules", response_model=project.createSchedule_service.CreateScheduleResponse
)
async def api_post_createSchedule(
    professionalId: int,
    startTime: datetime,
    endTime: datetime,
    activityType: str,
    isActive: bool,
) -> project.createSchedule_service.CreateScheduleResponse | Response:
    """
    Enables the creation of a new schedule entry for a professional. It accepts details such as time slots, professional ID, and activity type. This endpoint requires proper validations to avoid conflicts in the scheduling logic. Upon successful creation, it triggers an interaction with the Notification Engine to alert the professional of a new schedule entry.
    """
    try:
        res = await project.createSchedule_service.createSchedule(
            professionalId, startTime, endTime, activityType, isActive
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/user/favorites",
    response_model=project.removeUserFavorite_service.RemoveFavoriteResponse,
)
async def api_delete_removeUserFavorite(
    professionalId: int,
) -> project.removeUserFavorite_service.RemoveFavoriteResponse | Response:
    """
    Removes a professional from the user's list of favorites. Needs the professional's ID for removal. Confirms the removal with an updated list of favorites.
    """
    try:
        res = await project.removeUserFavorite_service.removeUserFavorite(
            professionalId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/users/{userId}", response_model=project.updateUser_service.UserUpdateResponse
)
async def api_put_updateUser(
    userId: str, email: Optional[str], password: Optional[str]
) -> project.updateUser_service.UserUpdateResponse | Response:
    """
    Updates details of a specific user. This allows users to update their own profiles, such as changing their password or email. The endpoint checks for authentication and authorization before permitting the update. It ensures data validation before committing any changes.
    """
    try:
        res = await project.updateUser_service.updateUser(userId, email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/users", response_model=project.createUser_service.CreateUserResponse)
async def api_post_createUser(
    name: str, email: str, password: str, role: prisma.enums.Role
) -> project.createUser_service.CreateUserResponse | Response:
    """
    Creates a new user account. This endpoint will collect user data such as name, email, and password, and store them securely. The response will confirm the creation of the user or provide error messages for invalid inputs. It uses standard security measures like hashing passwords before storage.
    """
    try:
        res = await project.createUser_service.createUser(name, email, password, role)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/schedules/{scheduleId}",
    response_model=project.deleteSchedule_service.DeleteScheduleResponse,
)
async def api_delete_deleteSchedule(
    scheduleId: int, requesterRole: prisma.enums.Role
) -> project.deleteSchedule_service.DeleteScheduleResponse | Response:
    """
    Removes a schedule entry from the system using the schedule ID. This operation must ensure that it cleans up all associated data and releases any booked resources or slots. Notifications are sent to affected parties to advise them of the cancellation.
    """
    try:
        res = await project.deleteSchedule_service.deleteSchedule(
            scheduleId, requesterRole
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/availability/{professionalId}",
    response_model=project.getProfessionalAvailability_service.AvailabilityResponse,
)
async def api_get_getProfessionalAvailability(
    request: project.getProfessionalAvailability_service.FetchAvailabilityRequest,
) -> project.getProfessionalAvailability_service.AvailabilityResponse | Response:
    """
    Retrieves real-time availability for a specific professional by their unique ID. This function connects to the Schedule Management module to pull detailed availability status for the requested professional. Ideal for users needing detailed, individual data.
    """
    try:
        res = await project.getProfessionalAvailability_service.getProfessionalAvailability(
            request
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/availability",
    response_model=project.getAvailability_service.FetchAvailabilityResponse,
)
async def api_get_getAvailability(
    request: project.getAvailability_service.FetchAvailabilityRequest,
) -> project.getAvailability_service.FetchAvailabilityResponse | Response:
    """
    Fetches real-time availability data of professionals. This endpoint queries the Schedule Management module to retrieve current activity or scheduled data. It is expected to return a list of professionals along with their current availability status. The response is dynamically updated as the Schedule Management data changes.
    """
    try:
        res = await project.getAvailability_service.getAvailability(request)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/user/profile", response_model=project.getUserProfile_service.UserProfileResponse
)
async def api_get_getUserProfile(
    user_id: int,
) -> project.getUserProfile_service.UserProfileResponse | Response:
    """
    Retrieves the user profile data including booked appointments and favorite professionals. It integrates with the Schedule Management to pull the latest booking details. Response includes user ID, name, email, booked appointments, and favorites list.
    """
    try:
        res = await project.getUserProfile_service.getUserProfile(user_id)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get("/users/{userId}", response_model=project.getUser_service.UserProfileResponse)
async def api_get_getUser(
    userId: int,
) -> project.getUser_service.UserProfileResponse | Response:
    """
    Retrieves details of a specific user by their unique identifier (userId). This is used to allow a user or admin to view user profiles. If the user is looking up their own profile, it returns the full profile; if an admin is viewing, it includes additional administrative fields.
    """
    try:
        res = await project.getUser_service.getUser(userId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
