"""MELCloud Home API client - refactored version."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiohttp import ClientSession

from .config import BASE_URL, DEFAULT_CACHE_DURATION_MINUTES, ENDPOINT_USER_CONTEXT
from .models import Device, UserProfile
from .services import ApiClient, AuthenticationService, DeviceService, UserDataCache

logger = logging.getLogger(__name__)


class MelCloudHomeClient:
    """
    Main client for MELCloud Home API.

    This client provides a high-level interface for interacting with the
    MELCloud Home platform, handling authentication, device management,
    and data caching.
    """

    def __init__(
        self,
        session: ClientSession | None = None,
        cache_duration_minutes: int = DEFAULT_CACHE_DURATION_MINUTES,
    ):
        """
        Initialize MELCloud Home client.

        Args:
            session: Optional HTTP session to use. If None, creates a new one.
            cache_duration_minutes: How long to cache user data
        """
        self._setup_session(session)
        self._setup_services(cache_duration_minutes)

    def _setup_session(self, session: ClientSession | None) -> None:
        """Setup HTTP session management."""
        if session:
            self._session = session
            self._manages_session = False
        else:
            self._session = ClientSession(base_url=BASE_URL, auto_decompress=False)
            self._manages_session = True

    def _setup_services(self, cache_duration_minutes: int) -> None:
        """Initialize all service components."""
        self._api_client = ApiClient(self._session)
        self._auth_service = AuthenticationService(self._session)
        self._cache = UserDataCache(cache_duration_minutes)
        self._device_service = DeviceService(self._api_client)

    async def __aenter__(self) -> "MelCloudHomeClient":
        """Enter async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit async context manager and cleanup resources."""
        await self.close()

    async def login(self, email: str, password: str) -> None:
        """
        Authenticate with MELCloud Home.

        Args:
            email: User's email address
            password: User's password
        """
        await self._auth_service.login(email, password)
        await self._refresh_user_profile()

    async def list_devices(self) -> list[Device]:
        """
        Get all devices associated with the user account.

        Returns:
            List of all devices
        """
        await self._ensure_user_profile_is_current()
        user_profile = self._cache.get_user_profile()

        if not user_profile:
            return []

        return self._device_service.extract_devices_from_profile(user_profile)

    async def get_device_state(self, device_id: str) -> dict[str, Any] | None:
        """
        Get current state of a specific device.

        Args:
            device_id: Unique identifier of the device

        Returns:
            Dictionary of device settings or None if device not found
        """
        await self._ensure_user_profile_is_current()
        user_profile = self._cache.get_user_profile()

        return self._device_service.get_device_state_by_id(user_profile, device_id)

    async def set_device_state(
        self, device_id: str, device_type: str, state_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update the state of a specific device.

        Args:
            device_id: Unique identifier of the device
            device_type: Type of device ('ataunit' or 'atwunit')
            state_data: New state data to apply

        Returns:
            API response confirming the update
        """
        response = await self._make_authenticated_request(
            lambda: self._device_service.update_device_state(
                device_id, device_type, state_data
            )
        )

        # Invalidate cache to ensure fresh data on next request
        self._cache.invalidate_cache()
        return response  # type: ignore[no-any-return]

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        if self._manages_session:
            await self._session.close()

    async def _ensure_user_profile_is_current(self) -> None:
        """Ensure we have current user profile data."""
        if not self._cache.is_cache_valid():
            await self._refresh_user_profile()

    async def _refresh_user_profile(self) -> None:
        """Fetch fresh user profile data from the API."""
        response = await self._make_authenticated_request(
            lambda: self._api_client.make_request("get", ENDPOINT_USER_CONTEXT)
        )

        user_profile = UserProfile.model_validate(response)
        self._cache.set_user_profile(user_profile)

    async def _make_authenticated_request(
        self, request_func: Callable[[], Awaitable[Any]]
    ) -> Any:
        """
        Make an API request with automatic re-authentication on session expiry.

        Args:
            request_func: Function that makes the actual API request

        Returns:
            The result of the request function
        """
        from .errors import ApiError

        try:
            return await request_func()
        except ApiError as e:
            # Check if this is a session expiry error
            if (
                self._api_client.is_session_expired(e.status)
                and await self._auth_service.can_retry_login()
            ):
                logger.debug("Retrying request after re-authentication")
                await self._auth_service.retry_login()
                await self._refresh_user_profile()
                return await request_func()
            raise
