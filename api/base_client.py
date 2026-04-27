from __future__ import annotations

import time
from collections.abc import Iterable
from typing import Any, TypeVar

import requests
from requests import Response
from requests.exceptions import RequestException

from api.response_models import ApiResponseModel
from config import API_REQUEST_RETRIES, REQUEST_RETRY_BACKOFF_SEC, REQUEST_TIMEOUT_SEC

SuccessModelT = TypeVar("SuccessModelT", bound=ApiResponseModel)
ErrorModelT = TypeVar("ErrorModelT", bound=ApiResponseModel)


class BaseApiClient:
    RETRYABLE_STATUSES = {500, 502, 503, 504}

    def __init__(self, session: requests.Session, base_url: str) -> None:
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json_data: dict[str, Any] | None = None,
        expected_status: int | Iterable[int] = 200,
        success_model: type[SuccessModelT] | None = None,
        error_model: type[ErrorModelT] | None = None,
    ) -> requests.Response | SuccessModelT | ErrorModelT:
        allowed_statuses = (
            {expected_status}
            if isinstance(expected_status, int)
            else set(expected_status)
        )
        request_url = f"{self.base_url}/{endpoint.lstrip('/')}"
        last_response: Response | None = None
        last_exception: RequestException | None = None

        for attempt in range(1, API_REQUEST_RETRIES + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=request_url,
                    json=json_data,
                    timeout=REQUEST_TIMEOUT_SEC,
                )
            except RequestException as error:
                last_exception = error
                if attempt < API_REQUEST_RETRIES:
                    time.sleep(REQUEST_RETRY_BACKOFF_SEC * attempt)
                    continue
                raise AssertionError(
                    f"Запрос {method} {request_url} завершился ошибкой после всех повторных попыток. "
                    f"Последнее исключение: {error.__class__.__name__}: {error}"
                ) from error

            last_response = response
            last_exception = None

            if response.status_code in allowed_statuses:
                selected_model: type[ApiResponseModel] | None = None
                if 200 <= response.status_code < 300:
                    selected_model = success_model
                elif 400 <= response.status_code < 600:
                    selected_model = error_model

                if selected_model is not None:
                    payload = self._parse_response_payload(response)
                    return selected_model.from_payload(payload)

                return response

            if (
                response.status_code in self.RETRYABLE_STATUSES
                and attempt < API_REQUEST_RETRIES
            ):
                time.sleep(REQUEST_RETRY_BACKOFF_SEC * attempt)
                continue

            raise AssertionError(
                f"Неожиданный статус {response.status_code} для {method} {response.request.url}. "
                f"Ожидался один из {sorted(allowed_statuses)}. Ответ: {response.text}"
            )

        raise AssertionError(
            f"Запрос {method} {request_url} завершился ошибкой после всех повторных попыток. "
            f"Последний ответ: {last_response.text if last_response is not None else 'ответ отсутствует'}. "
            f"Последнее исключение: {last_exception!r}"
        )

    @staticmethod
    def _parse_response_payload(response: requests.Response) -> Any:
        if not response.text.strip():
            return None
        try:
            return response.json()
        except ValueError as error:
            raise AssertionError(
                f"Ответ {response.request.method} {response.request.url} должен быть JSON, "
                f"но получено: {response.text}"
            ) from error
