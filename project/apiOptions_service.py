from pydantic import BaseModel


class CheckAvailabilityOptionsResponse(BaseModel):
    """
    Provides necessary information about the 'check availability' endpoint such as supported HTTP methods, necessary headers, and other related requirements.
    """

    allow: str
    access_control_allow_methods: str
    access_control_allow_headers: str


def apiOptions(
    access_control_request_method: str, access_control_request_headers: str
) -> CheckAvailabilityOptionsResponse:
    """
    Provides details about the supported methods and requirements for the check availability endpoint.
    It responds with accepted request formats and other API usage policies.
    This is useful for developer integrations and troubleshooting.

    Args:
        access_control_request_method (str): Used in CORS pre-flight requests to determine which HTTP method
                                             the app intends to use when making the actual request.
        access_control_request_headers (str): Used in CORS pre-flight requests to indicate which headers
                                              the app will use in the actual request.

    Returns:
        CheckAvailabilityOptionsResponse: Provides necessary information about the 'check availability' endpoint
                                          such as supported HTTP methods, necessary headers, and other related requirements.
    """
    methods = "OPTIONS, GET"
    headers = "Content-Type, Authorization"
    allow_methods = methods if access_control_request_method in methods else "OPTIONS"
    return CheckAvailabilityOptionsResponse(
        allow=allow_methods,
        access_control_allow_methods=methods,
        access_control_allow_headers=headers + ", " + access_control_request_headers,
    )
