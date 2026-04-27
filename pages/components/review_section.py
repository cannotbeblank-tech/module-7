from __future__ import annotations

import allure
from playwright.sync_api import Locator, Page

from data.models import ReviewData
from pages.actions import PageActions


class ReviewSection(PageActions):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def title(self) -> Locator:
        return self.page.locator("xpath=//main//*[self::h1 or self::h2 or self::h3][normalize-space()='Отзывы:']")

    @property
    def section_root(self) -> Locator:
        return self.title.locator("xpath=parent::*")

    @property
    def review_textarea(self) -> Locator:
        return self.section_root.locator("textarea[name='text']")

    @property
    def rating_select(self) -> Locator:
        return self.section_root.locator("xpath=.//button[@role='combobox']")

    @property
    def submit_button(self) -> Locator:
        return self.section_root.locator("xpath=.//button[@type='submit' and normalize-space()='Отправить']")

    @property
    def empty_state(self) -> Locator:
        return self.section_root.locator(
            "xpath=.//p[normalize-space()='Отзывов нет. Оставьте отзыв первым!']"
        )

    @property
    def review_author_titles(self) -> Locator:
        return self.section_root.locator("xpath=.//h4")

    @allure.step("Убедиться, что секция отзывов загружена")
    def assert_loaded(self) -> None:
        self.expect_visible(self.title)

    @allure.step("Оставить отзыв под фильмом")
    def leave_review(self, review: ReviewData) -> None:
        self.expect_visible(self.review_textarea)
        self.fill(self.review_textarea, review.text)
        self.select_option_by_text(self.rating_select, str(review.rating))
        self.click(self.submit_button)

    @allure.step("Проверить, что оставленный отзыв отображается в списке")
    def assert_review_present(self, reviewer_name: str, review: ReviewData) -> None:
        reviewer_heading = self.review_author_titles.locator(
            f"xpath=self::h4[normalize-space()={self._xpath_literal(reviewer_name)}]"
        )
        review_card = reviewer_heading.locator(
            "xpath=ancestor::div[.//h3[contains(normalize-space(),'Реи')]][1]"
        )
        self.expect_visible(review_card)
        self.expect_contains_text(review_card, reviewer_name)
        self.expect_contains_text(review_card, review.text)
        self.expect_contains_text(review_card, f"{review.rating}/5")
        self.expect_hidden(self.empty_state)

    @staticmethod
    def _xpath_literal(value: str) -> str:
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'

        parts = value.split("'")
        concat_parts: list[str] = []
        for index, part in enumerate(parts):
            concat_parts.append(f"'{part}'")
            if index < len(parts) - 1:
                concat_parts.append('"\'"')
        return f"concat({', '.join(concat_parts)})"
