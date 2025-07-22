"""MELCloud Home API access."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from aiohttp import ClientError, ClientSession
from playwright.async_api import async_playwright
from yarl import URL

from .errors import ApiError, DeviceNotFound, LoginError
from .models import Device, UserProfile

BASE_URL = "https://www.melcloudhome.com/api/"


class MelCloudHomeClient:
    """MELCloud Home client."""

    def __init__(
        self,
        session: Optional[ClientSession] = None,
        cache_duration_minutes: int = 5,
    ):
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
        self._cache_duration = timedelta(minutes=cache_duration_minutes)
        self._base_headers: Dict[str, Any] = {
            "x-csrf": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
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
                raise LoginError(
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

    async def _api_request(self, method: str, url: str, **kwargs) -> dict:
        """Make an API request, with automatic re-login on session expiry."""
        try:
            response = await self._session.request(method, url, **kwargs)
            if response.status == 401:
                # Session expired, attempt to re-login
                if not self._email or not self._password:
                    raise LoginError("Cannot re-login, credentials not stored.")

                await self.login(self._email, self._password)
                # Retry the request
                response = await self._session.request(method, url, **kwargs)

            if not response.ok:
                try:
                    error_message = await response.json()
                except ClientError:
                    error_message = await response.text()
                raise ApiError(response.status, error_message)

            return await response.json()
        except ClientError as e:
            status = getattr(e, "status", -1)
            raise ApiError(status, str(e)) from e

    async def _fetch_context(self):
        """Fetch the user context from the API."""
        response = await self._api_request(
            "get", "user/context", headers=self._base_headers
        )
        self._user_profile = UserProfile.model_validate(response)
        self._last_updated = datetime.now()

    async def _update_context_if_stale(self):
        """Fetch the user context if it's missing or expired."""
        if not self._user_profile or (
            self._last_updated
            and (datetime.now() - self._last_updated) > self._cache_duration
        ):
            await self._fetch_context()

    async def list_devices(self) -> List[Device]:
        """List all devices."""
        await self._update_context_if_stale()

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

    async def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of a specific device from the cached context."""
        await self._update_context_if_stale()

        if not self._user_profile:
            # This should not be reached if _update_context_if_stale is called
            raise LoginError("User profile is not available.")

        all_devices = []
        for building in self._user_profile.buildings:
            all_devices.extend(building.air_to_air_units)
            all_devices.extend(building.air_to_water_units)

        for device in all_devices:
            if device.id == device_id:
                return {setting.name: setting.value for setting in device.settings}

        return None

    async def set_device_state(
        self, device_id: str, device_type: str, state_data: dict
    ):
        """Update the state of a specific device."""
        if not device_type:
            raise DeviceNotFound("Device type is not set for this device.")

        api_url = f"{device_type}/{device_id}"

        response = await self._api_request(
            "put", api_url, headers=self._base_headers, json=state_data
        )

        # Invalidate cache to ensure latest state is fetched next time
        self._last_updated = None
        return response

    async def close(self):
        """Close the client session."""
        if self._managed_session:
            await self._session.close()
