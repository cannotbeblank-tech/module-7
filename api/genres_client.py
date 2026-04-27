from __future__ import annotations

import requests

from api.base_client import BaseApiClient
from api.response_models import ApiErrorResponse, GenreListResponse
from config import API_BASE_URL


class GenresClient(BaseApiClient):
    def __init__(self, session: requests.Session) -> None:
        super().__init__(session=session, base_url=API_BASE_URL)

    def get_genres(self, expected_status: int = 200) -> GenreListResponse | ApiErrorResponse:
        return self._request(
            "GET",
            "/genres",
            expected_status=expected_status,
            success_model=GenreListResponse,
            error_model=ApiErrorResponse,
        )
