from __future__ import annotations

import allure
import re
from playwright.sync_api import Locator, Page

from config import UI_BASE_URL
from pages.actions import PageActions


class BasePage(PageActions):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.base_url = UI_BASE_URL

    @property
    def header(self) -> Locator:
        return self.page.locator("xpath=//header")

    @property
    def home_link(self) -> Locator:
        return self.header.locator("xpath=.//a[@href='/' and normalize-space()='Cinescope']")

    @property
    def all_movies_link(self) -> Locator:
        return self.header.locator("xpath=.//a[@href='/movies' and normalize-space()='Все фильмы']")

    @allure.step("Перейти на главную страницу через шапку сайта")
    def go_to_home_page(self) -> None:
        self.click(self.home_link)
        self.page.wait_for_url(re.compile(f"^{re.escape(self.base_url)}/?$"))
        self.wait_for_client_hydration()

    @allure.step("Перейти на страницу всех фильмов через шапку сайта")
    def go_to_all_movies_page(self) -> None:
        self.click(self.all_movies_link)
        self.page.wait_for_url(re.compile(f"^{re.escape(self.base_url)}/movies/?$"))
        self.wait_for_client_hydration()
