from __future__ import annotations

import requests

from api.base_client import BaseApiClient
from api.response_models import ApiErrorResponse, MovieResponse
from config import API_BASE_URL


class MoviesClient(BaseApiClient):
    def __init__(self, session: requests.Session) -> None:
        super().__init__(session=session, base_url=API_BASE_URL)

    def create_movie(
        self,
        payload: dict,
        expected_status: int = 201,
    ) -> MovieResponse | ApiErrorResponse:
        return self._request(
            "POST",
            "/movies",
            json_data=payload,
            expected_status=expected_status,
            success_model=MovieResponse,
            error_model=ApiErrorResponse,
        )

    def delete_movie(self, movie_id: int, expected_status: int = 200) -> MovieResponse | ApiErrorResponse:
        return self._request(
            "DELETE",
            f"/movies/{movie_id}",
            expected_status=expected_status,
            success_model=MovieResponse,
            error_model=ApiErrorResponse,
        )
