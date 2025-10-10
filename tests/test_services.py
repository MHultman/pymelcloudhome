"""Tests for the services package components."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from pymelcloudhome.services import ApiClient, UserDataCache, DeviceService
from pymelcloudhome.models import UserProfile, Device, Building, Setting, Capabilities
from pymelcloudhome.errors import ApiError, DeviceNotFound, LoginError


class TestUserDataCache:
    """Test the UserDataCache service."""

    def test_cache_initialization(self):
        """Test cache is properly initialized."""
        cache = UserDataCache(cache_duration_minutes=10)
        
        assert cache.get_user_profile() is None
        assert not cache.is_cache_valid()
        assert not cache.has_user_profile()

    def test_set_and_get_user_profile(self):
        """Test setting and getting user profile."""
        cache = UserDataCache()
        
        # Create a mock user profile
        profile = UserProfile(
            id="test-id",
            firstname="Test",
            lastname="User",
            email="test@example.com",
            language="en",
            numberOfDevicesAllowed=10,
            numberOfBuildingsAllowed=2,
            numberOfGuestUsersAllowedPerUnit=5,
            numberOfGuestDevicesAllowed=10,
            buildings=[],
            guestBuildings=[],
            scenes=[]
        )
        
        cache.set_user_profile(profile)
        
        assert cache.get_user_profile() == profile
        assert cache.has_user_profile()
        assert cache.is_cache_valid()

    def test_cache_expiry(self):
        """Test that cache expires correctly."""
        cache = UserDataCache(cache_duration_minutes=0)  # Expire immediately
        
        profile = UserProfile(
            id="test-id",
            firstname="Test",
            lastname="User",
            email="test@example.com",
            language="en",
            numberOfDevicesAllowed=10,
            numberOfBuildingsAllowed=2,
            numberOfGuestUsersAllowedPerUnit=5,
            numberOfGuestDevicesAllowed=10,
            buildings=[],
            guestBuildings=[],
            scenes=[]
        )
        
        cache.set_user_profile(profile)
        
        # Profile should still be there
        assert cache.has_user_profile()
        
        # But cache should be invalid due to 0 minute duration
        import time
        time.sleep(0.1)  # Wait a bit
        assert not cache.is_cache_valid()

    def test_cache_invalidation(self):
        """Test manual cache invalidation."""
        cache = UserDataCache()
        
        profile = UserProfile(
            id="test-id",
            firstname="Test",
            lastname="User",
            email="test@example.com",
            language="en",
            numberOfDevicesAllowed=10,
            numberOfBuildingsAllowed=2,
            numberOfGuestUsersAllowedPerUnit=5,
            numberOfGuestDevicesAllowed=10,
            buildings=[],
            guestBuildings=[],
            scenes=[]
        )
        
        cache.set_user_profile(profile)
        assert cache.is_cache_valid()
        
        cache.invalidate_cache()
        assert not cache.is_cache_valid()
        # Profile should still be there, just marked as invalid
        assert cache.has_user_profile()


class TestDeviceService:
    """Test the DeviceService."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client."""
        return AsyncMock(spec=ApiClient)

    @pytest.fixture
    def device_service(self, mock_api_client):
        """Create device service with mock API client."""
        return DeviceService(mock_api_client)

    @pytest.fixture
    def sample_device(self):
        """Create a sample device for testing."""
        return Device(
            id="test-device-id",
            givenDisplayName="Test Device",
            displayIcon="TestIcon",
            settings=[
                Setting(name="Power", value="True"),
                Setting(name="Temperature", value="22")
            ],
            macAddress="00:11:22:33:44:55",
            timeZone="UTC",
            rssi=75,
            ftcModel=1,
            schedule=[],
            scheduleEnabled=True,
            frostProtection=None,
            overheatProtection=None,
            holidayMode=None,
            isConnected=True,
            isInError=False,
            capabilities=Capabilities(
                maxImportPower=1000,
                maxHeatOutput=2000,
                temperatureUnit="C",
                hasHotWater=True,
                immersionHeaterCapacity=500,
                minSetTankTemperature=40,
                maxSetTankTemperature=60,
                minSetTemperature=16,
                maxSetTemperature=30,
                temperatureIncrement=0.5,
                temperatureIncrementOverride="",
                hasHalfDegrees=True,
                hasZone2=False,
                hasDualRoomTemperature=False,
                hasThermostatZone1=True,
                hasThermostatZone2=False,
                hasHeatZone1=True,
                hasHeatZone2=False,
                hasMeasuredEnergyConsumption=True,
                hasMeasuredEnergyProduction=False,
                hasEstimatedEnergyConsumption=True,
                hasEstimatedEnergyProduction=False,
                ftcModel=1,
                refridgerentAddress=1,
                hasDemandSideControl=False
            )
        )

    @pytest.fixture
    def sample_user_profile(self, sample_device):
        """Create a sample user profile with devices."""
        building = Building(
            id="building-id",
            name="Test Building",
            timezone="UTC",
            airToAirUnits=[],
            airToWaterUnits=[sample_device]
        )
        
        return UserProfile(
            id="user-id",
            firstname="Test",
            lastname="User",
            email="test@example.com",
            language="en",
            numberOfDevicesAllowed=10,
            numberOfBuildingsAllowed=2,
            numberOfGuestUsersAllowedPerUnit=5,
            numberOfGuestDevicesAllowed=10,
            buildings=[building],
            guestBuildings=[],
            scenes=[]
        )

    def test_extract_devices_from_profile(self, device_service, sample_user_profile):
        """Test extracting devices from user profile."""
        devices = device_service.extract_devices_from_profile(sample_user_profile)
        
        assert len(devices) == 1
        assert devices[0].device_type == "atwunit"
        assert devices[0].id == "test-device-id"

    def test_find_device_by_id(self, device_service, sample_user_profile):
        """Test finding a device by ID."""
        device = device_service.find_device_by_id(sample_user_profile, "test-device-id")
        
        assert device is not None
        assert device.id == "test-device-id"

    def test_find_device_by_id_not_found(self, device_service, sample_user_profile):
        """Test finding a device that doesn't exist."""
        device = device_service.find_device_by_id(sample_user_profile, "nonexistent-id")
        
        assert device is None

    def test_extract_device_state(self, device_service, sample_device):
        """Test extracting device state."""
        state = device_service.extract_device_state(sample_device)
        
        expected_state = {"Power": "True", "Temperature": "22"}
        assert state == expected_state

    def test_get_device_state_by_id(self, device_service, sample_user_profile):
        """Test getting device state by ID."""
        state = device_service.get_device_state_by_id(sample_user_profile, "test-device-id")
        
        expected_state = {"Power": "True", "Temperature": "22"}
        assert state == expected_state

    def test_get_device_state_by_id_not_found(self, device_service, sample_user_profile):
        """Test getting device state for non-existent device."""
        state = device_service.get_device_state_by_id(sample_user_profile, "nonexistent-id")
        
        assert state is None

    def test_get_device_state_by_id_no_profile(self, device_service):
        """Test getting device state with no user profile."""
        with pytest.raises(LoginError):
            device_service.get_device_state_by_id(None, "test-device-id")

    @pytest.mark.asyncio
    async def test_update_device_state(self, device_service, mock_api_client):
        """Test updating device state."""
        mock_api_client.make_request.return_value = {"status": "ok"}
        
        result = await device_service.update_device_state(
            "test-device-id", 
            "atwunit", 
            {"Power": "False"}
        )
        
        assert result == {"status": "ok"}
        mock_api_client.make_request.assert_called_once_with(
            "put", 
            "atwunit/test-device-id", 
            json={"Power": "False"}
        )

    @pytest.mark.asyncio
    async def test_update_device_state_no_device_type(self, device_service):
        """Test updating device state with empty device type."""
        with pytest.raises(DeviceNotFound):
            await device_service.update_device_state(
                "test-device-id", 
                "", 
                {"Power": "False"}
            )


class TestApiClient:
    """Test the ApiClient service."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock aiohttp session."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def api_client(self, mock_session):
        """Create API client with mock session."""
        return ApiClient(mock_session)

    @pytest.mark.asyncio
    async def test_successful_request(self, api_client, mock_session):
        """Test successful API request."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "test"}
        mock_session.request.return_value = mock_response
        
        result = await api_client.make_request("GET", "/test")
        
        assert result == {"data": "test"}
        mock_session.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_failed_request_with_json_error(self, api_client, mock_session):
        """Test API request that fails with JSON error response."""
        # Mock failed response
        mock_response = AsyncMock()
        mock_response.ok = False
        mock_response.status = 400
        mock_response.json.return_value = {"error": "Bad Request"}
        mock_session.request.return_value = mock_response
        
        with pytest.raises(ApiError) as exc_info:
            await api_client.make_request("GET", "/test")
        
        assert exc_info.value.status == 400
        assert "Bad Request" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_failed_request_with_text_error(self, api_client, mock_session):
        """Test API request that fails with text error response."""
        from aiohttp import ClientError
        
        # Mock failed response that can't return JSON
        mock_response = AsyncMock()
        mock_response.ok = False
        mock_response.status = 500
        mock_response.json.side_effect = ClientError("JSON decode error")
        mock_response.text.return_value = "Internal Server Error"
        mock_session.request.return_value = mock_response
        
        with pytest.raises(ApiError) as exc_info:
            await api_client.make_request("GET", "/test")
        
        assert exc_info.value.status == 500
        assert "Internal Server Error" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_client_error_during_request(self, api_client, mock_session):
        """Test handling of client errors during request."""
        from aiohttp import ClientError
        
        # Mock client error during request
        mock_session.request.side_effect = ClientError("Connection error")
        
        with pytest.raises(ApiError) as exc_info:
            await api_client.make_request("GET", "/test")
        
        assert "Connection error" in str(exc_info.value.message)

    def test_is_session_expired(self, api_client):
        """Test session expiry detection."""
        assert api_client.is_session_expired(401) is True
        assert api_client.is_session_expired(400) is False
        assert api_client.is_session_expired(500) is False

    @pytest.mark.asyncio
    async def test_request_with_custom_headers(self, api_client, mock_session):
        """Test request with custom headers."""
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "test"}
        mock_session.request.return_value = mock_response
        
        custom_headers = {"Authorization": "Bearer token"}
        
        await api_client.make_request("GET", "/test", headers=custom_headers)
        
        # Verify the request was made with merged headers
        call_args = mock_session.request.call_args
        headers_used = call_args[1]["headers"]
        
        # Should contain both default and custom headers
        assert "x-csrf" in headers_used  # Default header
        assert "Authorization" in headers_used  # Custom header
        assert headers_used["Authorization"] == "Bearer token"