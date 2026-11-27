
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Get the default DRF error response
    response = exception_handler(exc, context)

    # If DRF cannot handle the exception, leave it unhandled
    if response is None:
        return None

    data = response.data

    # Handle validation errors
    if isinstance(data, dict) and "detail" not in data:
        message = "Validation failed."
        errors = data

    # Handle authentication, permission and other API errors
    elif isinstance(data, dict):
        detail = data.get("detail", "An error occurred.")
        message = str(detail)
        errors = None

    else:
        message = "An error occurred."
        errors = data

    # Standard response structure
    response.data = {
        "success": False,
        "message": message,
        "errors": errors
    }

    return response
