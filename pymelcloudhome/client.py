"""MELCloud Home API access."""

from datetime import datetime, timedelta
from typing import List, Optional

from aiohttp import ClientSession
from playwright.async_api import async_playwright
from yarl import URL

from .models import Device, UserProfile

BASE_URL = "https://www.melcloudhome.com/api/"


class MelCloudHomeClient:
    """MELCloud Home client."""

    def __init__(self, session: Optional[ClientSession] = None):
        """Initialize MELCloud Home client."""
        if session:
            self._session = session
            self._managed_session = False
        else:
            self._session = ClientSession(base_url=BASE_URL, auto_decompress=False)
            self._managed_session = True
        self._user_profile: Optional[UserProfile] = None
        self._last_updated: Optional[datetime] = None

    async def __aenter__(self):
        """Enter the async context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context and close the session."""
        await self.close()

    async def login(self, email: str, password: str):
        """Login to MELCloud Home using a headless browser to handle JavaScript."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            await page.goto(
                "https://www.melcloudhome.com/bff/login?returnUrl=/dashboard"
            )

            visible_form = page.locator('form[name="cognitoSignInForm"]:visible')

            await visible_form.locator('input[name="username"]').fill(email)
            await visible_form.locator('input[name="password"]').fill(password)

            await visible_form.locator('input[name="signInSubmitButton"]').click()

            try:
                await page.wait_for_url("**/dashboard", timeout=30000)
            except Exception as e:
                raise ConnectionError(
                    f"Login failed. Did not redirect to dashboard. Error: {e}"
                )

            browser_cookies = await context.cookies()
            for cookie in browser_cookies:
                cookie_url = URL(f"https://{cookie['domain']}")
                self._session.cookie_jar.update_cookies(
                    {cookie["name"]: cookie["value"]}, response_url=cookie_url
                )

            await browser.close()
            await self._fetch_context()

    async def _fetch_context(self):
        api_url = "user/context"

        api_headers = {
            "accept": "*/*",
            "referer": "https://www.melcloudhome.com/dashboard",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-csrf": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        }

        response = await self._session.get(api_url, headers=api_headers)
        response.raise_for_status()
        self._user_profile = UserProfile.model_validate(await response.json())
        self._last_updated = datetime.now()

    async def list_devices(self) -> List[Device]:
        """List all devices."""
        if not self._user_profile or (
            self._last_updated
            and (datetime.now() - self._last_updated) > timedelta(minutes=5)
        ):
            await self._fetch_context()

        devices = []
        if self._user_profile:
            for building in self._user_profile.buildings:
                devices.extend(building.air_to_air_units)
                devices.extend(building.air_to_water_units)
        return devices

    async def close(self):
        """Close the client session."""
        if self._managed_session:
            await self._session.close()
