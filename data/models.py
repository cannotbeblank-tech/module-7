from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UiUser:
    id: str
    email: str
    password: str
    full_name: str


@dataclass(frozen=True)
class MovieData:
    id: int
    name: str


@dataclass(frozen=True)
class ReviewData:
    text: str
    rating: int

    def __post_init__(self) -> None:
        normalized_text = self.text.strip()
        if not normalized_text:
            raise ValueError("Текст отзыва не должен быть пустым")
        if not 1 <= self.rating <= 5:
            raise ValueError("Оценка отзыва должна быть в диапазоне от 1 до 5")
