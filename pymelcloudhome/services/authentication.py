"""Authentication service for MELCloud Home."""

import logging

from aiohttp import ClientSession
from pyppeteer import launch
from pyppeteer.page import Page
from yarl import URL

from ..config import (
    DEFAULT_CHROMIUM_EXECUTABLE_PATH,
    DEFAULT_USER_AGENT,
    LOGIN_TIMEOUT_MILLISECONDS,
    LOGIN_URL,
)
from ..errors import LoginError

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Handles authentication with MELCloud Home using browser automation."""

    def __init__(
        self, session: ClientSession, chromium_executable_path: str | None = None
    ):
        """Initialize the authentication service.

        Args:
            session: aiohttp ClientSession for HTTP requests
            chromium_executable_path: Path to Chromium executable.
                None = use pyppeteer's bundled Chromium (won't work on ARM64).
                For ARM64/Raspberry Pi, provide system Chromium path, e.g.:
                - Debian/Ubuntu: '/usr/bin/chromium-browser'
                - Alpine Linux: '/usr/bin/chromium'
                - macOS ARM: '/Applications/Chromium.app/Contents/MacOS/Chromium'
        """
        self._session = session
        self._email: str | None = None
        self._password: str | None = None
        self._chromium_executable_path = (
            chromium_executable_path or DEFAULT_CHROMIUM_EXECUTABLE_PATH
        )

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

        await self._perform_browser_login(email, password)

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

    async def _perform_browser_login(self, email: str, password: str) -> None:
        """Perform the actual browser-based login."""
        launch_options = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-setuid-sandbox"],
        }

        # Use custom Chromium path if provided (required for ARM64/Raspberry Pi)
        if self._chromium_executable_path:
            launch_options["executablePath"] = self._chromium_executable_path
            logger.info("Using custom Chromium at: %s", self._chromium_executable_path)

        browser = await launch(**launch_options)
        try:
            page = await browser.newPage()
            await page.setUserAgent(DEFAULT_USER_AGENT)

            await self._navigate_to_login_page(page)
            await self._fill_login_form(page, email, password)
            await self._submit_login_form(page)
            await self._wait_for_successful_login(page)
            await self._transfer_cookies_to_session(page)

        finally:
            await browser.close()

    async def _navigate_to_login_page(self, page: Page) -> None:
        """Navigate to the login page."""
        await page.goto(LOGIN_URL)

    async def _fill_login_form(self, page: Page, email: str, password: str) -> None:
        """Fill in the login form with credentials."""
        await page.waitForSelector(
            'form[name="cognitoSignInForm"] input[name="username"]', visible=True
        )
        await page.type('form[name="cognitoSignInForm"] input[name="username"]', email)
        await page.type(
            'form[name="cognitoSignInForm"] input[name="password"]', password
        )

    async def _submit_login_form(self, page: Page) -> None:
        """Submit the login form."""
        await page.click(
            'form[name="cognitoSignInForm"] input[name="signInSubmitButton"]'
        )

    async def _wait_for_successful_login(self, page: Page) -> None:
        """Wait for redirect to dashboard to confirm successful login.

        After form submission, the browser navigates through AWS Cognito back to dashboard.
        The dashboard is a Blazor WebAssembly app that loads dynamically on the same page,
        so we may already be on the dashboard URL when waitForNavigation times out.
        """
        try:
            # Wait for navigation with timeout (may timeout if already on dashboard)
            await page.waitForNavigation(timeout=LOGIN_TIMEOUT_MILLISECONDS)
        except Exception as e:
            # Navigation timeout is expected if Blazor app loads on same page
            logger.debug("Navigation wait completed with exception: %s", e)

        # Check if we're on the dashboard (regardless of timeout)
        current_url = page.url
        if "/dashboard" in current_url:
            logger.info("Login successful - on dashboard: %s", current_url)
            return

        # If not on dashboard, login failed
        logger.error(
            "Login failed - redirected to %s instead of dashboard", current_url
        )
        raise LoginError(
            f"Login failed. Redirected to {current_url} instead of dashboard"
        )

    async def _transfer_cookies_to_session(self, page: Page) -> None:
        """Transfer authentication cookies from browser to HTTP session."""
        browser_cookies = await page.cookies()
        for cookie in browser_cookies:
            cookie_url = URL(f"https://{cookie.get('domain', '')}")
            name = cookie.get("name")
            value = cookie.get("value")
            if (
                name is not None
                and value is not None
                and isinstance(name, str)
                and isinstance(value, str)
            ):
                self._session.cookie_jar.update_cookies(
                    {name: value}, response_url=cookie_url
                )
