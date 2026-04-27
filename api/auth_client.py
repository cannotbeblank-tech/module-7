from __future__ import annotations

import requests

from api.base_client import BaseApiClient
from api.response_models import ApiErrorResponse, AuthResponse
from config import AUTH_BASE_URL, AUTH_REFRESH_COOKIE_NAME


class AuthClient(BaseApiClient):
    def __init__(self, session: requests.Session) -> None:
        super().__init__(session=session, base_url=AUTH_BASE_URL)

    def authenticate(
        self,
        email: str,
        password: str,
        expected_status: int = 200,
    ) -> AuthResponse | ApiErrorResponse:
        response = self._request(
            "POST",
            "/login",
            json_data={"email": email, "password": password},
            expected_status=expected_status,
            success_model=AuthResponse,
            error_model=ApiErrorResponse,
        )
        if isinstance(response, ApiErrorResponse):
            return response

        self.session.headers.update({"Authorization": f"Bearer {response.access_token}"})
        return response

    def get_refresh_token(self, email: str, password: str) -> str:
        auth_response = self.authenticate(email, password)
        if isinstance(auth_response, ApiErrorResponse):
            raise AssertionError(
                f"Авторизация завершилась ошибкой вместо успешного ответа: {auth_response.message}"
            )

        refresh_token = self.session.cookies.get(AUTH_REFRESH_COOKIE_NAME)
        if not refresh_token:
            raise AssertionError(
                f"Авторизация должна возвращать cookie '{AUTH_REFRESH_COOKIE_NAME}' для подготовки UI-сессии"
            )
        return refresh_token
