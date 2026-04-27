from __future__ import annotations

from uuid import uuid4

from faker import Faker

from data.models import ReviewData

faker = Faker("ru_RU")


class TestDataFactory:
    DEFAULT_TEST_USER_PASSWORD = "Qwerty123"

    @staticmethod
    def build_verified_user_payload() -> dict:
        email = f"ui_review_{uuid4()}@example.com"
        full_name = f"Автотест Отзыв {faker.first_name()} {faker.last_name()}"
        return {
            "email": email,
            "fullName": full_name,
            "password": TestDataFactory.DEFAULT_TEST_USER_PASSWORD,
            "passwordRepeat": TestDataFactory.DEFAULT_TEST_USER_PASSWORD,
            "verified": True,
            "banned": False,
            "roles": ["USER"],
        }

    @staticmethod
    def build_movie_payload(*, genre_id: int) -> dict:
        suffix = uuid4().hex[:8]
        return {
            "name": f"Фильм для отзыва {suffix}",
            "imageUrl": "https://example.com/image.png",
            "price": 100,
            "description": f"Фильм, созданный для UI-теста отзыва {suffix}",
            "location": "MSK",
            "published": True,
            "genreId": genre_id,
        }

    @staticmethod
    def build_review_data() -> ReviewData:
        suffix = uuid4().hex[:8]
        return ReviewData(text=f"Автотестовый отзыв {suffix}", rating=4)
