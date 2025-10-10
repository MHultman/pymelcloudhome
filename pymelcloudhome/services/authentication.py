"""Authentication service for MELCloud Home."""

import logging

from aiohttp import ClientSession
from playwright.async_api import async_playwright
from yarl import URL

from ..config import (
    DASHBOARD_URL_PATTERN,
    DEFAULT_USER_AGENT,
    LOGIN_TIMEOUT_MILLISECONDS,
    LOGIN_URL,
)
from ..errors import LoginError

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Handles authentication with MELCloud Home using browser automation."""

    def __init__(self, session: ClientSession):
        """Initialize the authentication service."""
        self._session = session
        self._email: str | None = None
        self._password: str | None = None

    async def login(self, email: str, password: str) -> None:
        """
        Authenticate with MELCloud Home using credentials.

        Args:
            email: User's email address
            password: User's password

        Raises:
            LoginError: If authentication fails
        """
        logger.info("Initiating login process for user: %s", email)
        self._store_credentials(email, password)

        async with async_playwright() as playwright:
            await self._perform_browser_login(playwright, email, password)

    async def can_retry_login(self) -> bool:
        """Check if we have stored credentials for retry."""
        return bool(self._email and self._password)

    async def retry_login(self) -> None:
        """Retry login with stored credentials."""
        if not await self.can_retry_login():
            raise LoginError("Cannot re-login, credentials not stored.")

        logger.warning("Session expired, attempting re-login")
        await self.login(self._email, self._password)  # type: ignore

    def _store_credentials(self, email: str, password: str) -> None:
        """Store credentials for potential retry."""
        self._email = email
        self._password = password

    async def _perform_browser_login(
        self, playwright, email: str, password: str
    ) -> None:
        """Perform the actual browser-based login."""
        browser = await playwright.chromium.launch()
        try:
            context = await browser.new_context(user_agent=DEFAULT_USER_AGENT)
            page = await context.new_page()

            await self._navigate_to_login_page(page)
            await self._fill_login_form(page, email, password)
            await self._submit_login_form(page)
            await self._wait_for_successful_login(page)
            await self._transfer_cookies_to_session(context)

        finally:
            await browser.close()

    async def _navigate_to_login_page(self, page) -> None:
        """Navigate to the login page."""
        await page.goto(LOGIN_URL)

    async def _fill_login_form(self, page, email: str, password: str) -> None:
        """Fill in the login form with credentials."""
        visible_form = page.locator('form[name="cognitoSignInForm"]:visible')
        await visible_form.locator('input[name="username"]').fill(email)
        await visible_form.locator('input[name="password"]').fill(password)

    async def _submit_login_form(self, page) -> None:
        """Submit the login form."""
        visible_form = page.locator('form[name="cognitoSignInForm"]:visible')
        await visible_form.locator('input[name="signInSubmitButton"]').click()

    async def _wait_for_successful_login(self, page) -> None:
        """Wait for redirect to dashboard to confirm successful login."""
        try:
            await page.wait_for_url(
                DASHBOARD_URL_PATTERN, timeout=LOGIN_TIMEOUT_MILLISECONDS
            )
            logger.info("Login successful - redirected to dashboard")
        except Exception as e:
            logger.error("Login failed - did not redirect to dashboard: %s", e)
            raise LoginError(
                f"Login failed. Did not redirect to dashboard. Error: {e}"
            ) from e

    async def _transfer_cookies_to_session(self, context) -> None:
        """Transfer authentication cookies from browser to HTTP session."""
        browser_cookies = await context.cookies()
        for cookie in browser_cookies:
            cookie_url = URL(f"https://{cookie.get('domain', '')}")
            name = cookie.get("name")
            value = cookie.get("value")
            if name is not None and value is not None:
                self._session.cookie_jar.update_cookies(
                    {name: value}, response_url=cookie_url
                )
