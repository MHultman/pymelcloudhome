"""Tests for the authentication service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientSession

from pymelcloudhome.services.authentication import AuthenticationService
from pymelcloudhome.errors import LoginError


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
        with patch('pymelcloudhome.services.authentication.async_playwright') as mock_playwright:
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance
            
            # Mock browser and page interactions
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()
            
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            mock_context.cookies.return_value = []
            
            # Mock successful login flow
            mock_page.wait_for_url = AsyncMock()
            mock_form = AsyncMock()
            mock_page.locator.return_value = mock_form
            
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
        mock_page = MagicMock()
        mock_form = MagicMock()
        mock_username_field = MagicMock()
        mock_password_field = MagicMock()
        
        # Make fill() async but not return a coroutine
        mock_username_field.fill = AsyncMock(return_value=None)
        mock_password_field.fill = AsyncMock(return_value=None)
        
        mock_page.locator.return_value = mock_form
        mock_form.locator.side_effect = [mock_username_field, mock_password_field]
        
        await auth_service._fill_login_form(mock_page, "test@example.com", "password123")
        
        mock_username_field.fill.assert_called_once_with("test@example.com")
        mock_password_field.fill.assert_called_once_with("password123")

    @pytest.mark.asyncio
    async def test_submit_login_form(self, auth_service):
        """Test submitting the login form."""
        mock_page = MagicMock()
        mock_form = MagicMock()
        mock_submit_button = MagicMock()
        
        # Make click() async but not return a coroutine
        mock_submit_button.click = AsyncMock(return_value=None)
        
        mock_page.locator.return_value = mock_form
        mock_form.locator.return_value = mock_submit_button
        
        await auth_service._submit_login_form(mock_page)
        
        mock_submit_button.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_wait_for_successful_login_success(self, auth_service):
        """Test successful login wait."""
        mock_page = AsyncMock()
        mock_page.wait_for_url = AsyncMock()
        
        # Should not raise an exception
        await auth_service._wait_for_successful_login(mock_page)
        
        mock_page.wait_for_url.assert_called_once_with("**/dashboard", timeout=30000)

    @pytest.mark.asyncio
    async def test_wait_for_successful_login_failure(self, auth_service):
        """Test failed login wait."""
        mock_page = AsyncMock()
        mock_page.wait_for_url.side_effect = Exception("Timeout")
        
        with pytest.raises(LoginError, match="Login failed"):
            await auth_service._wait_for_successful_login(mock_page)

    @pytest.mark.asyncio
    async def test_transfer_cookies_to_session(self, auth_service, mock_session):
        """Test transferring cookies from browser to session."""
        mock_context = AsyncMock()
        mock_context.cookies.return_value = [
            {
                "name": "session_id",
                "value": "abc123",
                "domain": "melcloudhome.com"
            },
            {
                "name": "csrf_token", 
                "value": "xyz789",
                "domain": "melcloudhome.com"
            }
        ]
        
        mock_session.cookie_jar = MagicMock()
        
        await auth_service._transfer_cookies_to_session(mock_context)
        
        # Should have called update_cookies twice (once for each cookie)
        assert mock_session.cookie_jar.update_cookies.call_count == 2

    @pytest.mark.asyncio
    async def test_transfer_cookies_handles_invalid_cookies(self, auth_service, mock_session):
        """Test that invalid cookies are skipped."""
        mock_context = AsyncMock()
        mock_context.cookies.return_value = [
            {
                "name": None,  # Invalid cookie
                "value": "abc123",
                "domain": "melcloudhome.com"
            },
            {
                "name": "valid_cookie",
                "value": None,  # Invalid cookie
                "domain": "melcloudhome.com"
            },
            {
                "name": "good_cookie",
                "value": "xyz789",
                "domain": "melcloudhome.com"
            }
        ]
        
        mock_session.cookie_jar = MagicMock()
        
        await auth_service._transfer_cookies_to_session(mock_context)
        
        # Should only have called update_cookies once (for the valid cookie)
        assert mock_session.cookie_jar.update_cookies.call_count == 1