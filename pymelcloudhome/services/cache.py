"""Cache management for user data."""

import logging
from datetime import datetime, timedelta

from ..models import UserProfile

logger = logging.getLogger(__name__)


class UserDataCache:
    """Manages caching of user profile and related data."""

    def __init__(self, cache_duration_minutes: int = 5):
        """Initialize the cache with specified duration."""
        self._user_profile: UserProfile | None = None
        self._last_updated: datetime | None = None
        self._cache_duration = timedelta(minutes=cache_duration_minutes)

    def get_user_profile(self) -> UserProfile | None:
        """Get the cached user profile."""
        return self._user_profile

    def set_user_profile(self, profile: UserProfile) -> None:
        """Store user profile in cache."""
        self._user_profile = profile
        self._last_updated = datetime.now()
        logger.debug("User profile cached successfully")

    def is_cache_valid(self) -> bool:
        """Check if the cached data is still valid."""
        if not self._user_profile or not self._last_updated:
            return False

        time_since_update = datetime.now() - self._last_updated
        is_valid = time_since_update <= self._cache_duration

        if not is_valid:
            logger.debug("Cache expired, needs refresh")

        return is_valid

    def invalidate_cache(self) -> None:
        """Invalidate the current cache."""
        self._last_updated = None
        logger.debug("Cache invalidated")

    def has_user_profile(self) -> bool:
        """Check if we have a cached user profile."""
        return self._user_profile is not None
