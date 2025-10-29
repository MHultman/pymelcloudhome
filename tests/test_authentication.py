"""Tests for the authentication service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession

from pymelcloudhome.errors import LoginError
from pymelcloudhome.services.authentication import AuthenticationService


class TestAuthenticationService:
    """Test the AuthenticationService."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock aiohttp session."""
        return AsyncMock(spec=ClientSession)

    @pytest.fixture
    def auth_service(self, mock_session):
        """Create authentication service with mock session."""
        return AuthenticationService(mock_session)

    def test_initialization(self, auth_service, mock_session):
        """Test service initialization."""
        assert auth_service._session == mock_session
        assert auth_service._email is None
        assert auth_service._password is None

    @pytest.mark.asyncio
    async def test_can_retry_login_false_initially(self, auth_service):
        """Test that retry login returns False when no credentials stored."""
        can_retry = await auth_service.can_retry_login()
        assert can_retry is False

    @pytest.mark.asyncio
    async def test_can_retry_login_true_after_login_attempt(self, auth_service):
        """Test that retry login returns True after credentials are stored."""
        # Mock the browser login process
        with patch("pymelcloudhome.services.authentication.launch") as mock_launch:
            # Mock browser and page interactions
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_launch.return_value = mock_browser
            mock_browser.newPage.return_value = mock_page
            mock_browser.close = AsyncMock()

            # Mock page methods
            mock_page.setUserAgent = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.waitForSelector = AsyncMock()
            mock_page.type = AsyncMock()
            mock_page.click = AsyncMock()
            mock_page.waitForNavigation = AsyncMock()
            mock_page.url = "https://www.melcloudhome.com/dashboard"
            mock_page.cookies = AsyncMock(return_value=[])

            try:
                await auth_service.login("test@example.com", "password123")
            except Exception:
                pass  # We expect this to potentially fail in the mock environment

        # Credentials should be stored regardless of login success/failure
        can_retry = await auth_service.can_retry_login()
        assert can_retry is True

    @pytest.mark.asyncio
    async def test_retry_login_without_credentials(self, auth_service):
        """Test that retry login fails when no credentials are stored."""
        with pytest.raises(LoginError, match="Cannot re-login, credentials not stored"):
            await auth_service.retry_login()

    @pytest.mark.asyncio
    async def test_store_credentials(self, auth_service):
        """Test credentials storage."""
        auth_service._store_credentials("test@example.com", "password123")

        assert auth_service._email == "test@example.com"
        assert auth_service._password == "password123"

    @pytest.mark.asyncio
    async def test_navigate_to_login_page(self, auth_service):
        """Test navigation to login page."""
        mock_page = AsyncMock()

        await auth_service._navigate_to_login_page(mock_page)

        mock_page.goto.assert_called_once_with(
            "https://www.melcloudhome.com/bff/login?returnUrl=/dashboard"
        )

    @pytest.mark.asyncio
    async def test_fill_login_form(self, auth_service):
        """Test filling the login form."""
        mock_page = AsyncMock()
        mock_page.waitForSelector = AsyncMock()
        mock_page.type = AsyncMock()

        await auth_service._fill_login_form(
            mock_page, "test@example.com", "password123"
        )

        # Verify waitForSelector was called
        mock_page.waitForSelector.assert_called_once_with(
            'form[name="cognitoSignInForm"] input[name="username"]', visible=True
        )

        # Verify type was called for both fields
        assert mock_page.type.call_count == 2
        mock_page.type.assert_any_call(
            'form[name="cognitoSignInForm"] input[name="username"]', "test@example.com"
        )
        mock_page.type.assert_any_call(
            'form[name="cognitoSignInForm"] input[name="password"]', "password123"
        )

    @pytest.mark.asyncio
    async def test_submit_login_form(self, auth_service):
        """Test submitting the login form."""
        mock_page = AsyncMock()
        mock_page.click = AsyncMock()

        await auth_service._submit_login_form(mock_page)

        mock_page.click.assert_called_once_with(
            'form[name="cognitoSignInForm"] input[name="signInSubmitButton"]'
        )

    @pytest.mark.asyncio
    async def test_wait_for_successful_login_success(self, auth_service):
        """Test successful login wait."""
        mock_page = AsyncMock()
        mock_page.waitForNavigation = AsyncMock()
        mock_page.url = "https://www.melcloudhome.com/dashboard"

        # Should not raise an exception
        await auth_service._wait_for_successful_login(mock_page)

        mock_page.waitForNavigation.assert_called_once_with(timeout=30000)

    @pytest.mark.asyncio
    async def test_wait_for_successful_login_failure(self, auth_service):
        """Test failed login wait."""
        mock_page = AsyncMock()
        mock_page.waitForNavigation = AsyncMock()
        mock_page.url = "https://auth.melcloudhome.com/login"  # Not on dashboard

        with pytest.raises(LoginError, match="Login failed"):
            await auth_service._wait_for_successful_login(mock_page)

    @pytest.mark.asyncio
    async def test_transfer_cookies_to_session(self, auth_service, mock_session):
        """Test transferring cookies from browser to session."""
        mock_page = AsyncMock()
        mock_page.cookies.return_value = [
            {"name": "session_id", "value": "abc123", "domain": "melcloudhome.com"},
            {"name": "csrf_token", "value": "xyz789", "domain": "melcloudhome.com"},
        ]

        mock_session.cookie_jar = MagicMock()

        await auth_service._transfer_cookies_to_session(mock_page)

        # Should have called update_cookies twice (once for each cookie)
        assert mock_session.cookie_jar.update_cookies.call_count == 2

    @pytest.mark.asyncio
    async def test_transfer_cookies_handles_invalid_cookies(
        self, auth_service, mock_session
    ):
        """Test that invalid cookies are skipped."""
        mock_page = AsyncMock()
        mock_page.cookies.return_value = [
            {
                "name": None,  # Invalid cookie
                "value": "abc123",
                "domain": "melcloudhome.com",
            },
            {
                "name": "valid_cookie",
                "value": None,  # Invalid cookie
                "domain": "melcloudhome.com",
            },
            {"name": "good_cookie", "value": "xyz789", "domain": "melcloudhome.com"},
        ]

        mock_session.cookie_jar = MagicMock()

        await auth_service._transfer_cookies_to_session(mock_page)

        # Should only have called update_cookies once (for the valid cookie)
        assert mock_session.cookie_jar.update_cookies.call_count == 1
