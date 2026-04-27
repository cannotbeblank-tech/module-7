from __future__ import annotations

import allure
import pytest
import requests

from api import AuthClient, GenresClient, MoviesClient, UsersClient
from api.mappers import map_movie_response_to_movie_data, map_user_response_to_ui_user
from config import (
    AUTH_BASE_URL,
    AUTH_REFRESH_COOKIE_NAME,
    DEFAULT_UI_TIMEOUT_MS,
    HEADLESS,
    SAVE_TRACE_FOR_PASSED_TESTS,
    SCREENSHOT_DIR,
    SUPER_ADMIN_EMAIL,
    SUPER_ADMIN_PASSWORD,
    TRACE_DIR,
)
from data import MovieData, ReviewData, TestDataFactory, UiUser
from pages import MoviePage
from utils import FileManager, assert_api_success


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(scope="session")
def browser(playwright):
    browser_instance = playwright.chromium.launch(headless=HEADLESS)
    yield browser_instance
    browser_instance.close()


@pytest.fixture(scope="function")
def context(browser, request):
    context_instance = browser.new_context(viewport={"width": 1600, "height": 900})
    context_instance.set_default_timeout(DEFAULT_UI_TIMEOUT_MS)
    context_instance.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context_instance

    should_persist_trace = SAVE_TRACE_FOR_PASSED_TESTS or (
        getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    )
    if should_persist_trace:
        trace_dir = FileManager.ensure_dir(TRACE_DIR)
        trace_path = trace_dir / f"{request.node.name}_{FileManager.timestamp()}.zip"
        context_instance.tracing.stop(path=str(trace_path))
        allure.attach.file(
            str(trace_path),
            name=trace_path.name,
            extension="zip",
        )
    else:
        context_instance.tracing.stop()
    context_instance.close()


@pytest.fixture(scope="function")
def page(context, request):
    page_instance = context.new_page()
    yield page_instance

    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        screenshot_dir = FileManager.ensure_dir(SCREENSHOT_DIR)
        screenshot_path = screenshot_dir / f"{request.node.name}_{FileManager.timestamp()}.png"
        page_instance.screenshot(path=str(screenshot_path), full_page=True)
        allure.attach.file(
            str(screenshot_path),
            name=screenshot_path.name,
            attachment_type=allure.attachment_type.PNG,
        )

    page_instance.close()


@pytest.fixture(scope="session")
def admin_session() -> requests.Session:
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope="session")
def admin_auth_client(admin_session: requests.Session) -> AuthClient:
    return AuthClient(admin_session)


@pytest.fixture(scope="session")
def admin_users_client(admin_session: requests.Session) -> UsersClient:
    return UsersClient(admin_session)


@pytest.fixture(scope="session")
def admin_movies_client(admin_session: requests.Session) -> MoviesClient:
    return MoviesClient(admin_session)


@pytest.fixture(scope="session", autouse=True)
def authenticate_super_admin(admin_auth_client: AuthClient) -> None:
    with allure.step("Авторизовать супер-админа для backend-подготовки данных"):
        assert_api_success(
            admin_auth_client.authenticate(SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD),
            "авторизация супер-админа",
        )


@pytest.fixture(scope="session")
def admin_genres_client(admin_session: requests.Session) -> GenresClient:
    return GenresClient(admin_session)


@pytest.fixture(scope="session")
def existing_genre_id(admin_genres_client: GenresClient) -> int:
    with allure.step("Получить существующий жанр для создания тестового фильма"):
        genres_response = assert_api_success(
            admin_genres_client.get_genres(),
            "получение жанров",
        )
        assert genres_response.genres, (
            "API Cinescope должен вернуть хотя бы один жанр для подготовки фильма"
        )
        return genres_response.genres[0].id


@pytest.fixture(scope="function")
def ui_user(admin_users_client: UsersClient) -> UiUser:
    with allure.step("Создать тестового пользователя через API"):
        payload = TestDataFactory.build_verified_user_payload()
        created_user_response = assert_api_success(
            admin_users_client.create_user(payload),
            "создание пользователя",
        )
        created_user = map_user_response_to_ui_user(
            created_user_response,
            password=payload["password"],
        )
        assert created_user.email == payload["email"]
    yield created_user
    with allure.step("Удалить тестового пользователя через API"):
        assert_api_success(
            admin_users_client.delete_user(created_user.id),
            "удаление пользователя",
        )


@pytest.fixture(scope="function")
def movie_under_test(admin_movies_client: MoviesClient, existing_genre_id: int) -> MovieData:
    with allure.step("Создать тестовый фильм через API"):
        payload = TestDataFactory.build_movie_payload(genre_id=existing_genre_id)
        created_movie_response = assert_api_success(
            admin_movies_client.create_movie(payload),
            "создание фильма",
        )
        created_movie = map_movie_response_to_movie_data(created_movie_response)
    yield created_movie
    with allure.step("Удалить тестовый фильм через API"):
        assert_api_success(
            admin_movies_client.delete_movie(created_movie.id),
            "удаление фильма",
        )


@pytest.fixture(scope="function")
def review_data() -> ReviewData:
    return TestDataFactory.build_review_data()


@pytest.fixture(scope="function")
def movie_page(page) -> MoviePage:
    return MoviePage(page)


@pytest.fixture(scope="function")
def authorized_ui_user(context, ui_user: UiUser) -> UiUser:
    with requests.Session() as user_session:
        with allure.step("Подготовить авторизованную UI-сессию пользователя через cookie"):
            auth_client = AuthClient(user_session)
            refresh_token = auth_client.get_refresh_token(ui_user.email, ui_user.password)

            context.add_cookies(
                [
                    {
                        "name": AUTH_REFRESH_COOKIE_NAME,
                        "value": refresh_token,
                        "url": AUTH_BASE_URL,
                    }
                ]
            )
    return ui_user
