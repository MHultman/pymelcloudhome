"""Integration tests for the complete client workflow."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import web

from pymelcloudhome.client import MelCloudHomeClient
from pymelcloudhome.errors import ApiError, LoginError


class TestClientIntegration:
    """Integration tests for the complete client workflow."""

    @pytest.fixture
    async def mock_client_with_auth(self, aiohttp_client):
        """Create a client with mocked authentication flow."""
        app = web.Application()

        async def context_handler(request):
            return web.json_response({
                "id": "user-id",
                "firstname": "Test",
                "lastname": "User", 
                "email": "test@example.com",
                "language": "en",
                "numberOfDevicesAllowed": 10,
                "numberOfBuildingsAllowed": 2,
                "numberOfGuestUsersAllowedPerUnit": 5,
                "numberOfGuestDevicesAllowed": 10,
                "buildings": [
                    {
                        "id": "building-id",
                        "name": "Test Building",
                        "timezone": "UTC",
                        "airToAirUnits": [
                            {
                                "id": "ata-device-id",
                                "givenDisplayName": "ATA Unit",
                                "displayIcon": "ATA",
                                "settings": [
                                    {"name": "Power", "value": "True"},
                                    {"name": "SetTemperature", "value": "22"}
                                ],
                                "macAddress": "00:11:22:33:44:55",
                                "timeZone": "UTC",
                                "rssi": 80,
                                "ftcModel": 1,
                                "schedule": [],
                                "scheduleEnabled": False,
                                "frostProtection": None,
                                "overheatProtection": None,
                                "holidayMode": None,
                                "isConnected": True,
                                "isInError": False,
                                "capabilities": {
                                    "maxImportPower": 0,
                                    "maxHeatOutput": 0,
                                    "temperatureUnit": "C",
                                    "hasHotWater": False,
                                    "immersionHeaterCapacity": 0,
                                    "minSetTankTemperature": 0,
                                    "maxSetTankTemperature": 0,
                                    "minSetTemperature": 16,
                                    "maxSetTemperature": 30,
                                    "temperatureIncrement": 1.0,
                                    "temperatureIncrementOverride": "",
                                    "hasHalfDegrees": False,
                                    "hasZone2": False,
                                    "hasDualRoomTemperature": False,
                                    "hasThermostatZone1": False,
                                    "hasThermostatZone2": False,
                                    "hasHeatZone1": False,
                                    "hasHeatZone2": False,
                                    "hasMeasuredEnergyConsumption": False,
                                    "hasMeasuredEnergyProduction": False,
                                    "hasEstimatedEnergyConsumption": False,
                                    "hasEstimatedEnergyProduction": False,
                                    "ftcModel": 1,
                                    "refridgerentAddress": 1,
                                    "hasDemandSideControl": False
                                }
                            }
                        ],
                        "airToWaterUnits": [
                            {
                                "id": "atw-device-id",
                                "givenDisplayName": "ATW Unit",
                                "displayIcon": "ATW",
                                "settings": [
                                    {"name": "Power", "value": "False"},
                                    {"name": "SetTemperatureZone1", "value": "20"}
                                ],
                                "macAddress": "00:11:22:33:44:56",
                                "timeZone": "UTC",
                                "rssi": 75,
                                "ftcModel": 2,
                                "schedule": [],
                                "scheduleEnabled": True,
                                "frostProtection": None,
                                "overheatProtection": None,
                                "holidayMode": None,
                                "isConnected": True,
                                "isInError": False,
                                "capabilities": {
                                    "maxImportPower": 1000,
                                    "maxHeatOutput": 2000,
                                    "temperatureUnit": "C",
                                    "hasHotWater": True,
                                    "immersionHeaterCapacity": 500,
                                    "minSetTankTemperature": 40,
                                    "maxSetTankTemperature": 60,
                                    "minSetTemperature": 16,
                                    "maxSetTemperature": 30,
                                    "temperatureIncrement": 0.5,
                                    "temperatureIncrementOverride": "",
                                    "hasHalfDegrees": True,
                                    "hasZone2": False,
                                    "hasDualRoomTemperature": False,
                                    "hasThermostatZone1": True,
                                    "hasThermostatZone2": False,
                                    "hasHeatZone1": True,
                                    "hasHeatZone2": False,
                                    "hasMeasuredEnergyConsumption": True,
                                    "hasMeasuredEnergyProduction": False,
                                    "hasEstimatedEnergyConsumption": True,
                                    "hasEstimatedEnergyProduction": False,
                                    "ftcModel": 2,
                                    "refridgerentAddress": 1,
                                    "hasDemandSideControl": False
                                }
                            }
                        ]
                    }
                ],
                "guestBuildings": [],
                "scenes": []
            })

        async def update_device_handler(request):
            return web.json_response({"status": "success"})

        app.router.add_get("/user/context", context_handler)
        app.router.add_put("/ataunit/ata-device-id", update_device_handler)
        app.router.add_put("/atwunit/atw-device-id", update_device_handler)

        return await aiohttp_client(app)

    @pytest.mark.asyncio
    async def test_complete_workflow(self, mock_client_with_auth):
        """Test complete client workflow from login to device control."""
        with patch('pymelcloudhome.services.authentication.async_playwright') as mock_playwright:
            # Mock the browser login process
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = MagicMock()
            
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            mock_context.cookies.return_value = []

            # Mock successful login flow
            mock_page.wait_for_url = AsyncMock(return_value=None)
            mock_page.goto = AsyncMock(return_value=None)
            mock_form = MagicMock()
            mock_username_field = MagicMock()
            mock_password_field = MagicMock()
            mock_submit_button = MagicMock()

            # Make async methods properly mockable
            mock_username_field.fill = AsyncMock(return_value=None)
            mock_password_field.fill = AsyncMock(return_value=None)
            mock_submit_button.click = AsyncMock(return_value=None)
            
            mock_page.locator.return_value = mock_form
            mock_form.locator.side_effect = [mock_username_field, mock_password_field, mock_submit_button]

            async with MelCloudHomeClient(session=mock_client_with_auth.session) as client:
                client._session._base_url = mock_client_with_auth.server.make_url("/")
                
                # Step 1: Login (mocked)
                await client.login("test@example.com", "password123")
                
                # Step 2: List devices
                devices = await client.list_devices()
                assert len(devices) == 2
                
                # Verify device types are set correctly
                ata_device = next(d for d in devices if d.id == "ata-device-id")
                atw_device = next(d for d in devices if d.id == "atw-device-id")
                
                assert ata_device.device_type == "ataunit"
                assert atw_device.device_type == "atwunit"
                
                # Step 3: Get device states
                ata_state = await client.get_device_state("ata-device-id")
                atw_state = await client.get_device_state("atw-device-id")
                
                assert ata_state is not None
                assert atw_state is not None
                assert ata_state["Power"] == "True"
                assert ata_state["SetTemperature"] == "22"
                assert atw_state["Power"] == "False"
                assert atw_state["SetTemperatureZone1"] == "20"
                
                # Step 4: Update device states
                ata_response = await client.set_device_state(
                    "ata-device-id", "ataunit", {"Power": "False"}
                )
                atw_response = await client.set_device_state(
                    "atw-device-id", "atwunit", {"Power": "True", "SetTemperatureZone1": "22"}
                )
                
                assert ata_response["status"] == "success"
                assert atw_response["status"] == "success"

    @pytest.mark.asyncio
    async def test_cache_behavior(self, mock_client_with_auth):
        """Test that caching works correctly."""
        with patch('pymelcloudhome.services.authentication.async_playwright') as mock_playwright:
            # Mock the browser login
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = MagicMock()
            
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            mock_context.cookies.return_value = []
            
            mock_page.wait_for_url = AsyncMock(return_value=None)
            mock_page.goto = AsyncMock(return_value=None)
            mock_form = MagicMock()
            mock_username_field = MagicMock()
            mock_password_field = MagicMock()
            mock_submit_button = MagicMock()

            # Make async methods properly mockable
            mock_username_field.fill = AsyncMock(return_value=None)
            mock_password_field.fill = AsyncMock(return_value=None)
            mock_submit_button.click = AsyncMock(return_value=None)

            mock_page.locator.return_value = mock_form
            mock_form.locator.side_effect = [mock_username_field, mock_password_field, mock_submit_button]

            async with MelCloudHomeClient(
                session=mock_client_with_auth.session,
                cache_duration_minutes=10  # Longer cache for testing
            ) as client:
                client._session._base_url = mock_client_with_auth.server.make_url("/")
                
                # Login and first device list - should hit API
                await client.login("test@example.com", "password123")
                devices1 = await client.list_devices()
                
                # Second device list - should use cache
                devices2 = await client.list_devices()
                
                # Should be identical (same data)
                assert len(devices1) == len(devices2)
                assert devices1[0].id == devices2[0].id
                
                # Force cache invalidation
                client._cache.invalidate_cache()
                
                # Third device list - should hit API again
                devices3 = await client.list_devices()
                assert len(devices3) == len(devices1)

    @pytest.mark.asyncio
    async def test_session_expiry_retry(self, aiohttp_client):
        """Test automatic retry on session expiry."""
        call_count = 0
        
        async def context_handler_with_auth_check(request):
            nonlocal call_count
            call_count += 1
            
            # First call returns 401 (session expired)
            if call_count == 1:
                return web.Response(status=401, text="Unauthorized")
            
            # Second call returns valid data (after re-auth)
            return web.json_response({
                "id": "user-id",
                "firstname": "Test",
                "lastname": "User",
                "email": "test@example.com",
                "language": "en",
                "numberOfDevicesAllowed": 10,
                "numberOfBuildingsAllowed": 2,
                "numberOfGuestUsersAllowedPerUnit": 5,
                "numberOfGuestDevicesAllowed": 10,
                "buildings": [],
                "guestBuildings": [],
                "scenes": []
            })

        app = web.Application()
        app.router.add_get("/user/context", context_handler_with_auth_check)
        test_client = await aiohttp_client(app)

        with patch('pymelcloudhome.services.authentication.async_playwright') as mock_playwright:
            # Mock browser login for both initial and retry
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = MagicMock()
            
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            mock_context.cookies.return_value = []
            
            mock_page.wait_for_url = AsyncMock(return_value=None)
            mock_page.goto = AsyncMock(return_value=None)
            mock_form = MagicMock()
            mock_username_field = MagicMock()
            mock_password_field = MagicMock()
            mock_submit_button = MagicMock()

            # Make async methods properly mockable
            mock_username_field.fill = AsyncMock(return_value=None)
            mock_password_field.fill = AsyncMock(return_value=None)
            mock_submit_button.click = AsyncMock(return_value=None)

            mock_page.locator.return_value = mock_form
            # Provide enough mock elements for both initial login and retry login (2 calls * 3 elements each)
            mock_form.locator.side_effect = [
                mock_username_field, mock_password_field, mock_submit_button,  # First login attempt
                mock_username_field, mock_password_field, mock_submit_button   # Retry login attempt
            ]

            async with MelCloudHomeClient(session=test_client.session) as client:
                client._session._base_url = test_client.server.make_url("/")
                
                # Initial login
                await client.login("test@example.com", "password123")
                
                # This should trigger session expiry, auto re-login, and succeed
                devices = await client.list_devices()
                
                # Should have succeeded after retry
                assert devices == []
                
                # Should have been called 3 times: 
                # 1. Initial login call (fails with 401)
                # 2. Retry login call (succeeds)  
                # 3. list_devices() refresh call (succeeds)
                assert call_count == 3

    @pytest.mark.asyncio
    async def test_device_not_found_during_state_get(self, mock_client_with_auth):
        """Test getting state for non-existent device."""
        with patch('pymelcloudhome.services.authentication.async_playwright') as mock_playwright:
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = MagicMock()
            
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            mock_context.cookies.return_value = []
            
            mock_page.wait_for_url = AsyncMock(return_value=None)
            mock_page.goto = AsyncMock(return_value=None)
            mock_form = MagicMock()
            mock_username_field = MagicMock()
            mock_password_field = MagicMock()
            mock_submit_button = MagicMock()

            # Make async methods properly mockable
            mock_username_field.fill = AsyncMock(return_value=None)
            mock_password_field.fill = AsyncMock(return_value=None)
            mock_submit_button.click = AsyncMock(return_value=None)

            mock_page.locator.return_value = mock_form
            mock_form.locator.side_effect = [mock_username_field, mock_password_field, mock_submit_button]

            async with MelCloudHomeClient(session=mock_client_with_auth.session) as client:
                client._session._base_url = mock_client_with_auth.server.make_url("/")
                
                await client.login("test@example.com", "password123")
                
                # Try to get state for non-existent device
                state = await client.get_device_state("nonexistent-device-id")
                assert state is None

    @pytest.mark.asyncio
    async def test_context_manager_closes_session(self):
        """Test that context manager properly closes managed session."""
        client = MelCloudHomeClient()  # Creates its own session
        
        # Mock the session close method
        client._session.close = AsyncMock(return_value=None)
        
        async with client:
            pass  # Just enter and exit context
        
        # Should have called close
        client._session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_does_not_close_external_session(self, mock_client_with_auth):
        """Test that context manager doesn't close externally provided session."""
        external_session = mock_client_with_auth.session
        external_session.close = AsyncMock(return_value=None)
        
        async with MelCloudHomeClient(session=external_session):
            pass
        
        # Should not have called close on external session
        external_session.close.assert_not_called()