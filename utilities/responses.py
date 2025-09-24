import typing

from django import forms
from django.http import JsonResponse


class ApiResponse(JsonResponse):
    def __init__(
        self, success: bool, status: int, **kwargs: typing.Dict[str, typing.Any]
    ):
        super().__init__(
            {
                "success": success,
                **kwargs,
            },
            status=status,
        )


class ApiSuccessResponse(ApiResponse):
    def __init__(self, payload: typing.Any = None, status: int = 200):
        kwargs = {}

        if payload is not None:
            kwargs["payload"] = payload

        super().__init__(
            success=True,
            status=status,
            **kwargs,
        )


class ApiSuccessKwargsResponse(ApiSuccessResponse):
    def __init__(self, status: int = 200, **kwargs: typing.Dict[str, typing.Any]):
        super().__init__(
            status=status,
            payload=kwargs,
        )


class ApiErrorResponse(ApiResponse):
    def __init__(self, error: typing.Any = None, status: int = 404):
        kwargs = {}

        if error is not None:
            kwargs["error"] = error

        super().__init__(
            success=False,
            status=status,
            **kwargs,
        )


class ApiErrorKwargsResponse(ApiErrorResponse):
    def __init__(self, status: int = 404, **kwargs: typing.Dict[str, typing.Any]):
        super().__init__(
            status=status,
            error=kwargs,
        )


class ApiErrorMessageAndCodeResponse(ApiErrorResponse):
    def __init__(
        self,
        message: str,
        code: int,
        status: int = 404,
    ):
        super().__init__(
            status=status,
            error={"message": message, "code": code},
        )


class ApiFormErrorResponse(ApiErrorResponse):
    def __init__(self, form: forms.Form, code: int = 1000, status: int = 400):
        super().__init__(
            status=status,
            error={
                "message": form.errors.as_data().popitem()[1][0].message,
                "code": code,
                "errors": form.errors,
            },
        )
