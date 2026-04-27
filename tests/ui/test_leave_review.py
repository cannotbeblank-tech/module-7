from __future__ import annotations

import allure
import pytest

from data import MovieData, ReviewData, UiUser
from pages import MoviePage


@allure.epic("Тестирование UI Cinescope")
@allure.feature("Отзывы под фильмом")
@pytest.mark.ui
@pytest.mark.review
class TestMovieReviews:
    @allure.title("Авторизованный пользователь может оставить отзыв под фильмом")
    @allure.story("Создание нового отзыва")
    def test_user_can_leave_review_under_movie(
        self,
        movie_page: MoviePage,
        authorized_ui_user: UiUser,
        movie_under_test: MovieData,
        review_data: ReviewData,
    ) -> None:
        movie_page.open(movie_under_test.id)
        movie_page.assert_movie_title(movie_under_test.name)
        movie_page.leave_review(review_data)
        movie_page.assert_review_visible_for_user(
            reviewer_name=authorized_ui_user.full_name,
            review=review_data,
        )
