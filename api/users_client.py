from __future__ import annotations

import requests

from api.base_client import BaseApiClient
from api.response_models import ApiErrorResponse, EmptySuccessResponse, UserResponse
from config import AUTH_BASE_URL


class UsersClient(BaseApiClient):
    def __init__(self, session: requests.Session) -> None:
        super().__init__(session=session, base_url=AUTH_BASE_URL)

    def create_user(
        self,
        payload: dict,
        expected_status: int = 201,
    ) -> UserResponse | ApiErrorResponse:
        return self._request(
            "POST",
            "/user",
            json_data=payload,
            expected_status=expected_status,
            success_model=UserResponse,
            error_model=ApiErrorResponse,
        )

    def delete_user(self, user_id: str, expected_status: int = 200) -> EmptySuccessResponse | ApiErrorResponse:
        return self._request(
            "DELETE",
            f"/user/{user_id}",
            expected_status=expected_status,
            success_model=EmptySuccessResponse,
            error_model=ApiErrorResponse,
        )
