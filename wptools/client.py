from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Dict, List
from urllib.parse import urljoin

import requests

from .exceptions import WPAuthenticationError, WPRequestError


logger = logging.getLogger(__name__)


@dataclass
class WPAdminCredentials:
    base_url: str
    username: str
    password: str
    timeout: int = 10


class WPAdminClient:
    """Simple WordPress admin client for authentication and data export."""

    def __init__(self, credentials: WPAdminCredentials) -> None:
        self.credentials = credentials
        self._session = requests.Session()
        self._is_authenticated = False

    @property
    def session(self) -> requests.Session:
        if not self._is_authenticated:
            raise WPAuthenticationError("Client is not authenticated. Call login() first.")
        return self._session

    def login(self) -> None:
        creds = self.credentials
        login_url = urljoin(self._normalized_base_url, "wp-login.php")
        payload = {
            "log": creds.username,
            "pwd": creds.password,
            "wp-submit": "Log In",
            "redirect_to": urljoin(self._normalized_base_url, "wp-admin/"),
            "testcookie": "1",
        }

        logger.debug("Attempting login at %s with user %s", login_url, creds.username)
        response = self._session.post(login_url, data=payload, timeout=creds.timeout, allow_redirects=True)

        logger.debug("Login response status: %s", response.status_code)
        logger.debug("Received cookies: %s", list(response.cookies.keys()))

        if not self._has_auth_cookie(response.cookies):
            raise WPAuthenticationError("Unable to authenticate with provided credentials.")

        self._is_authenticated = True

    def fetch_json(self, path: str, params: Dict[str, Any] | None = None) -> Any:
        url = urljoin(self._normalized_base_url, path)
        logger.debug("Fetching JSON from %s with params %s", url, params)
        response = self.session.get(url, params=params, timeout=self.credentials.timeout)
        if not response.ok:
            raise WPRequestError(
                f"Request to {url} failed with status {response.status_code}: {response.text}"
            )
        logger.debug("Response status for %s: %s", url, response.status_code)
        return response.json()

    def export_content(self) -> Dict[str, Any]:
        site_info = self.fetch_json("/wp-json")
        posts = self._fetch_collection("/wp-json/wp/v2/posts", params={"per_page": 100})
        pages = self._fetch_collection("/wp-json/wp/v2/pages", params={"per_page": 100})
        media = self._fetch_collection("/wp-json/wp/v2/media", params={"per_page": 100})
        categories = self._fetch_collection("/wp-json/wp/v2/categories", params={"per_page": 100})
        tags = self._fetch_collection("/wp-json/wp/v2/tags", params={"per_page": 100})

        return {
            "site": site_info,
            "posts": posts,
            "pages": pages,
            "media": media,
            "categories": categories,
            "tags": tags,
        }

    def _fetch_collection(self, path: str, params: Dict[str, Any] | None = None) -> List[Any]:
        params = params or {}
        items: List[Any] = []
        page = 1

        while True:
            page_params = {**params, "page": page}
            url = urljoin(self._normalized_base_url, path)
            logger.debug("Fetching collection page %s from %s with params %s", page, url, page_params)
            response = self.session.get(url, params=page_params, timeout=self.credentials.timeout)
            if not response.ok:
                raise WPRequestError(
                    f"Request to {url} failed with status {response.status_code}: {response.text}"
                )

            batch = response.json()
            logger.debug("Received %s items on page %s", len(batch), page)
            items.extend(batch)

            total_pages = int(response.headers.get("X-WP-TotalPages", 1))
            logger.debug("Total pages for %s: %s", url, total_pages)
            if page >= total_pages:
                break
            page += 1

        return items

    @property
    def _normalized_base_url(self) -> str:
        base = self.credentials.base_url.rstrip("/") + "/"
        return base

    @staticmethod
    def _has_auth_cookie(cookie_jar: requests.cookies.RequestsCookieJar) -> bool:
        return any(name.startswith("wordpress_logged_in") for name in cookie_jar.keys())
