from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass
from typing import Any, Protocol


class ApiResponseModel(Protocol):
    @classmethod
    def from_payload(cls, payload: Any) -> Any:
        ...


def _require_dict(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AssertionError(f"Ожидался JSON-объект, но получен {type(payload).__name__}")
    return payload


def _require_list(payload: Any) -> list[Any]:
    if not isinstance(payload, list):
        raise AssertionError(f"Ожидался JSON-массив, но получен {type(payload).__name__}")
    return payload


def _require_field(payload: dict[str, Any], field_name: str) -> Any:
    if field_name not in payload:
        raise AssertionError(f"JSON-ответ не содержит обязательное поле '{field_name}'")
    return payload[field_name]


def _require_non_empty_string(payload: dict[str, Any], field_name: str) -> str:
    value = _require_field(payload, field_name)
    if not isinstance(value, str) or not value.strip():
        raise AssertionError(f"Поле '{field_name}' должно быть непустой строкой")
    return value


def _require_string(payload: dict[str, Any], field_name: str) -> str:
    value = _require_field(payload, field_name)
    if not isinstance(value, str):
        raise AssertionError(f"Поле '{field_name}' должно быть строкой")
    return value


def _require_int(payload: dict[str, Any], field_name: str) -> int:
    value = _require_field(payload, field_name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise AssertionError(f"Поле '{field_name}' должно быть целым числом")
    return value


def _require_bool(payload: dict[str, Any], field_name: str) -> bool:
    value = _require_field(payload, field_name)
    if not isinstance(value, bool):
        raise AssertionError(f"Поле '{field_name}' должно быть булевым")
    return value


def _require_number(payload: dict[str, Any], field_name: str) -> float:
    value = _require_field(payload, field_name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AssertionError(f"Поле '{field_name}' должно быть числом")
    return float(value)


def _require_string_list(payload: dict[str, Any], field_name: str) -> list[str]:
    value = _require_field(payload, field_name)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise AssertionError(f"Поле '{field_name}' должно быть списком строк")
    return value


def _require_datetime(payload: dict[str, Any], field_name: str) -> datetime:
    value = _require_non_empty_string(payload, field_name)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise AssertionError(f"Поле '{field_name}' должно быть датой в ISO-формате") from error


@dataclass(frozen=True)
class ApiErrorResponse:
    message: str | list[str]

    @classmethod
    def from_payload(cls, payload: Any) -> ApiErrorResponse:
        payload_dict = _require_dict(payload)
        message = _require_field(payload_dict, "message")
        if isinstance(message, str):
            return cls(message=message)
        if isinstance(message, list) and all(isinstance(item, str) for item in message):
            return cls(message=message)
        raise AssertionError("Поле 'message' должно быть строкой или списком строк")


@dataclass(frozen=True)
class EmptySuccessResponse:
    @classmethod
    def from_payload(cls, payload: Any) -> EmptySuccessResponse:
        if payload not in (None, ""):
            raise AssertionError("Ожидалось пустое тело ответа")
        return cls()


@dataclass(frozen=True)
class AuthResponse:
    access_token: str

    @classmethod
    def from_payload(cls, payload: Any) -> AuthResponse:
        payload_dict = _require_dict(payload)
        return cls(access_token=_require_non_empty_string(payload_dict, "accessToken"))


@dataclass(frozen=True)
class GenreResponse:
    id: int
    name: str

    @classmethod
    def from_payload(cls, payload: Any) -> GenreResponse:
        payload_dict = _require_dict(payload)
        return cls(
            id=_require_int(payload_dict, "id"),
            name=_require_string(payload_dict, "name"),
        )


@dataclass(frozen=True)
class GenreListResponse:
    genres: list[GenreResponse]

    @classmethod
    def from_payload(cls, payload: Any) -> GenreListResponse:
        payload_list = _require_list(payload)
        return cls(genres=[GenreResponse.from_payload(item) for item in payload_list])


@dataclass(frozen=True)
class MovieGenreResponse:
    name: str

    @classmethod
    def from_payload(cls, payload: Any) -> MovieGenreResponse:
        payload_dict = _require_dict(payload)
        return cls(name=_require_string(payload_dict, "name"))


@dataclass(frozen=True)
class MovieResponse:
    id: int
    name: str
    price: int
    description: str
    image_url: str
    location: str
    published: bool
    rating: float
    genre_id: int
    created_at: datetime
    genre: MovieGenreResponse

    @classmethod
    def from_payload(cls, payload: Any) -> MovieResponse:
        payload_dict = _require_dict(payload)
        return cls(
            id=_require_int(payload_dict, "id"),
            name=_require_non_empty_string(payload_dict, "name"),
            price=_require_int(payload_dict, "price"),
            description=_require_non_empty_string(payload_dict, "description"),
            image_url=_require_non_empty_string(payload_dict, "imageUrl"),
            location=_require_non_empty_string(payload_dict, "location"),
            published=_require_bool(payload_dict, "published"),
            rating=_require_number(payload_dict, "rating"),
            genre_id=_require_int(payload_dict, "genreId"),
            created_at=_require_datetime(payload_dict, "createdAt"),
            genre=MovieGenreResponse.from_payload(_require_field(payload_dict, "genre")),
        )


@dataclass(frozen=True)
class UserResponse:
    id: str
    email: str
    full_name: str
    verified: bool
    banned: bool
    roles: list[str]
    created_at: datetime

    @classmethod
    def from_payload(cls, payload: Any) -> UserResponse:
        payload_dict = _require_dict(payload)
        return cls(
            id=_require_non_empty_string(payload_dict, "id"),
            email=_require_non_empty_string(payload_dict, "email"),
            full_name=_require_non_empty_string(payload_dict, "fullName"),
            verified=_require_bool(payload_dict, "verified"),
            banned=_require_bool(payload_dict, "banned"),
            roles=_require_string_list(payload_dict, "roles"),
            created_at=_require_datetime(payload_dict, "createdAt"),
        )
