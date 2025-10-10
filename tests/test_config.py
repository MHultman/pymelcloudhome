"""Tests for configuration constants."""

import pytest
from pymelcloudhome import config


class TestConfig:
    """Test configuration constants."""

    def test_api_urls(self):
        """Test API URL constants."""
        assert config.BASE_URL == "https://www.melcloudhome.com/api/"
        assert config.LOGIN_URL == "https://www.melcloudhome.com/bff/login?returnUrl=/dashboard"
        assert config.DASHBOARD_URL_PATTERN == "**/dashboard"

    def test_timeout_constants(self):
        """Test timeout and duration constants."""
        assert config.DEFAULT_CACHE_DURATION_MINUTES == 5
        assert config.LOGIN_TIMEOUT_MILLISECONDS == 30000

    def test_headers(self):
        """Test default headers."""
        assert "x-csrf" in config.DEFAULT_HEADERS
        assert "user-agent" in config.DEFAULT_HEADERS
        assert config.DEFAULT_HEADERS["x-csrf"] == "1"
        
        # Test that user agent contains expected browser info
        user_agent = config.DEFAULT_USER_AGENT
        assert "Mozilla" in user_agent
        assert "Chrome" in user_agent

    def test_device_types(self):
        """Test device type constants."""
        assert config.DEVICE_TYPE_AIR_TO_AIR == "ataunit"
        assert config.DEVICE_TYPE_AIR_TO_WATER == "atwunit"

    def test_endpoints(self):
        """Test API endpoint constants."""
        assert config.ENDPOINT_USER_CONTEXT == "user/context"