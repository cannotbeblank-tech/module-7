from __future__ import annotations

import allure
from playwright.sync_api import Locator, Page

from data.models import ReviewData
from pages.base_page import BasePage
from pages.components.review_section import ReviewSection


class MoviePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.review_section = ReviewSection(page)

    @property
    def movie_title(self) -> Locator:
        return self.page.locator("xpath=//main//section[1]//h2")

    @allure.step("Открыть страницу фильма с id={movie_id}")
    def open(self, movie_id: int) -> None:
        self.open_url(f"{self.base_url}/movies/{movie_id}")
        self.wait_for_client_hydration()
        self.review_section.assert_loaded()

    @allure.step("Проверить заголовок фильма")
    def assert_movie_title(self, movie_name: str) -> None:
        self.expect_contains_text(self.movie_title, movie_name)

    @allure.step("Оставить отзыв под фильмом")
    def leave_review(self, review: ReviewData) -> None:
        self.review_section.leave_review(review)

    @allure.step("Проверить, что отзыв пользователя отображается под фильмом")
    def assert_review_visible_for_user(self, reviewer_name: str, review: ReviewData) -> None:
        self.review_section.assert_review_present(reviewer_name=reviewer_name, review=review)
