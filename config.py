from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        name, value = line.split("=", 1)
        env_name = name.strip()
        if not env_name or env_name in os.environ:
            continue

        os.environ[env_name] = value.strip().strip('"').strip("'")


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Требуется переменная окружения {name}")
    return value


BASE_DIR = Path(__file__).resolve().parent
_load_dotenv_file(BASE_DIR / ".env")

ARTIFACTS_DIR = BASE_DIR / "artifacts"
TRACE_DIR = ARTIFACTS_DIR / "traces"
SCREENSHOT_DIR = ARTIFACTS_DIR / "screenshots"

UI_BASE_URL = os.getenv("UI_BASE_URL", "https://dev-cinescope.coconutqa.ru")
AUTH_BASE_URL = os.getenv("AUTH_BASE_URL", "https://auth.dev-cinescope.coconutqa.ru")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.dev-cinescope.coconutqa.ru")
AUTH_REFRESH_COOKIE_NAME = os.getenv("AUTH_REFRESH_COOKIE_NAME", "refresh_token")

SUPER_ADMIN_EMAIL = _get_required_env("SUPER_ADMIN_EMAIL")
SUPER_ADMIN_PASSWORD = _get_required_env("SUPER_ADMIN_PASSWORD")

DEFAULT_UI_TIMEOUT_MS = int(os.getenv("DEFAULT_UI_TIMEOUT_MS", "30000"))
REQUEST_TIMEOUT_SEC = int(os.getenv("REQUEST_TIMEOUT_SEC", "30"))
API_REQUEST_RETRIES = int(os.getenv("API_REQUEST_RETRIES", "3"))
REQUEST_RETRY_BACKOFF_SEC = float(os.getenv("REQUEST_RETRY_BACKOFF_SEC", "1"))
UI_NAVIGATION_RETRIES = int(os.getenv("UI_NAVIGATION_RETRIES", "3"))
HEADLESS = os.getenv("PWDEBUG") != "1"
SAVE_TRACE_FOR_PASSED_TESTS = os.getenv("SAVE_TRACE_FOR_PASSED_TESTS") == "1"
