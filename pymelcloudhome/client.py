"""MELCloud Home API access."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from aiohttp import ClientError, ClientSession
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
        self._email: Optional[str] = None
        self._password: Optional[str] = None
        self._base_headers: Dict[str, Any] = {
            "x-csrf": "1",
        }

    async def __aenter__(self):
        """Enter the async context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context and close the session."""
        await self.close()

    async def login(self, email: str, password: str):
        """Login to MELCloud Home using a headless browser to handle JavaScript."""
        self._email = email
        self._password = password
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(
                user_agent=self._base_headers["user-agent"]
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
                cookie_url = URL(f"https://{cookie.get('domain', '')}")
                name = cookie.get("name")
                value = cookie.get("value")
                if name is not None and value is not None:
                    self._session.cookie_jar.update_cookies(
                        {name: value}, response_url=cookie_url
                    )

            await browser.close()
            await self._fetch_context()

    async def _ensure_session_valid(self):
        """Ensure the session is valid, re-logging in if necessary."""
        if self._user_profile is not None:
            return

        if self._email and self._password:
            await self.login(self._email, self._password)
        else:
            raise ConnectionError("Not logged in.")

    async def _fetch_context(self):
        api_url = "user/context"
        api_headers = self._base_headers.copy()

        try:
            response = await self._session.get(api_url, headers=api_headers)
            response.raise_for_status()
            self._user_profile = UserProfile.model_validate(await response.json())
            self._last_updated = datetime.now()
        except ClientError:
            self._user_profile = None
            self._last_updated = None
            raise

    async def list_devices(self) -> List[Device]:
        """List all devices."""
        await self._ensure_session_valid()
        if not self._user_profile or (
            self._last_updated
            and (datetime.now() - self._last_updated) > timedelta(minutes=5)
        ):
            await self._fetch_context()

        devices = []
        if self._user_profile:
            for building in self._user_profile.buildings:
                for unit in building.air_to_air_units:
                    unit.device_type = "ataunit"
                    devices.append(unit)
                for unit in building.air_to_water_units:
                    unit.device_type = "atwunit"
                    devices.append(unit)
        return devices

    async def get_device_state(self, device_id: str):
        """Get the state of a specific device."""
        await self._ensure_session_valid()
        if not self._user_profile or (
            self._last_updated
            and (datetime.now() - self._last_updated) > timedelta(minutes=5)
        ):
            await self._fetch_context()

        if not self._user_profile:
            raise ValueError("User profile is not available. Please login first.")

        api_url = f"device/{device_id}/state"
        response = await self._session.get(api_url)
        response.raise_for_status()
        return await response.json()

    async def set_device_state(
        self, device_id: str, device_type: str, state_data: dict
    ):
        """Update the state of a specific device."""
        await self._ensure_session_valid()
        if not device_type:
            raise ValueError("Device type is not set for this device.")

        api_url = f"{device_type}/{device_id}"

        api_headers = self._base_headers.copy()

        response = await self._session.put(
            api_url, headers=api_headers, json=state_data
        )
        response.raise_for_status()
        # Invalidate cache to ensure latest state is fetched next time
        self._last_updated = None
        return await response.json()

    async def close(self):
        """Close the client session."""
        if self._managed_session:
            await self._session.close()
