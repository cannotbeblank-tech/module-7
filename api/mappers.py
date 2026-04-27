from __future__ import annotations

from api.response_models import MovieResponse, UserResponse
from data.models import MovieData, UiUser


def map_movie_response_to_movie_data(response: MovieResponse) -> MovieData:
    return MovieData(id=response.id, name=response.name)


def map_user_response_to_ui_user(response: UserResponse, password: str) -> UiUser:
    return UiUser(
        id=response.id,
        email=response.email,
        password=password,
        full_name=response.full_name,
    )
