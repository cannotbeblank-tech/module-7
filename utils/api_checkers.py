from __future__ import annotations

from typing import TypeVar

from api.response_models import ApiErrorResponse

ApiSuccessT = TypeVar("ApiSuccessT")


def assert_api_success(result: ApiSuccessT | ApiErrorResponse, action_name: str) -> ApiSuccessT:
    if isinstance(result, ApiErrorResponse):
        raise AssertionError(f"Не удалось выполнить действие '{action_name}' через API: {result.message}")
    return result
