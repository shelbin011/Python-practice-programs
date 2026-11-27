from rest_framework.response import Response


def success_response(
    data=None,
    message="Request successful.",
    status_code=200,
):
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status_code,
    )


class SuccessResponseMixin:
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)

        if not isinstance(response, Response):
            return response

        if (
            response.exception
            or not 200 <= response.status_code < 300
            or response.status_code == 204
        ):
            return response

        if (
            isinstance(response.data, dict)
            and response.data.get("success") is True
            and "message" in response.data
            and "data" in response.data
        ):
            return response

        response.data = success_response(
            data=response.data,
            status_code=response.status_code,
        ).data
        return response
