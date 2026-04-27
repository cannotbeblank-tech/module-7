from __future__ import annotations

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page, expect

from config import UI_NAVIGATION_RETRIES


class PageActions:
    RETRYABLE_NAVIGATION_ERRORS = (
        "ERR_NAME_NOT_RESOLVED",
        "ERR_CONNECTION_RESET",
        "ERR_CONNECTION_CLOSED",
        "ERR_CONNECTION_TIMED_OUT",
        "ERR_TIMED_OUT",
    )

    def __init__(self, page: Page) -> None:
        self.page = page

    def open_url(self, url: str) -> None:
        last_error: PlaywrightError | None = None

        for attempt in range(1, UI_NAVIGATION_RETRIES + 1):
            try:
                self.page.goto(url, wait_until="domcontentloaded")
                return
            except PlaywrightError as error:
                last_error = error
                error_text = str(error)
                is_retryable = any(
                    marker in error_text for marker in self.RETRYABLE_NAVIGATION_ERRORS
                )
                if is_retryable and attempt < UI_NAVIGATION_RETRIES:
                    continue
                raise

        if last_error is not None:
            raise last_error

    def wait_for_client_hydration(self) -> None:
        self.page.wait_for_function(
            "window[Symbol.for('radix-ui')] === true",
            timeout=10000,
        )

    def click(self, locator: Locator) -> None:
        locator.click()

    def fill(self, locator: Locator, value: str) -> None:
        locator.fill(value)

    def expect_visible(self, locator: Locator) -> None:
        expect(locator).to_be_visible()

    def expect_hidden(self, locator: Locator) -> None:
        expect(locator).to_be_hidden()

    def expect_count(self, locator: Locator, count: int) -> None:
        expect(locator).to_have_count(count)

    def expect_contains_text(self, locator: Locator, text: str) -> None:
        expect(locator).to_contain_text(text)

    def select_option_by_text(self, trigger: Locator, value: str) -> None:
        trigger.click()
        self.page.locator(f"xpath=//*[@role='option' and normalize-space()='{value}']").click()
