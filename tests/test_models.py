"""Tests for model validation and structure."""

import pytest
from pydantic import ValidationError

from pymelcloudhome.models.base import Capabilities, Setting
from pymelcloudhome.models.building import Building
from pymelcloudhome.models.device import Device
from pymelcloudhome.models.user import UserProfile


class TestSetting:
    """Test the Setting model."""

    def test_setting_creation(self):
        """Test creating a valid setting."""
        setting = Setting(name="Power", value="True")

        assert setting.name == "Power"
        assert setting.value == "True"

    def test_setting_validation_requires_name(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            Setting(value="True")  # type: ignore[call-arg]

    def test_setting_validation_requires_value(self):
        """Test that value is required."""
        with pytest.raises(ValidationError):
            Setting(name="Power")  # type: ignore[call-arg]


class TestCapabilities:
    """Test the Capabilities model."""

    @pytest.fixture
    def sample_capabilities_data(self):
        """Sample capabilities data."""
        return {
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
            "ftcModel": 1,
            "refridgerentAddress": 1,
            "hasDemandSideControl": False,
        }

    def test_capabilities_creation(self, sample_capabilities_data):
        """Test creating capabilities with all fields."""
        capabilities = Capabilities(**sample_capabilities_data)

        assert capabilities.max_import_power == 1000
        assert capabilities.has_hot_water is True
        assert capabilities.temperature_increment == 0.5
        assert capabilities.refrigerant_address == 1

    def test_capabilities_field_aliases(self, sample_capabilities_data):
        """Test that field aliases work correctly."""
        capabilities = Capabilities(**sample_capabilities_data)

        # Test some key aliases
        assert (
            capabilities.max_import_power == sample_capabilities_data["maxImportPower"]
        )
        assert capabilities.has_hot_water == sample_capabilities_data["hasHotWater"]
        assert (
            capabilities.min_set_temperature
            == sample_capabilities_data["minSetTemperature"]
        )

    def test_capabilities_missing_required_field(self, sample_capabilities_data):
        """Test that missing required fields raise validation error."""
        del sample_capabilities_data["maxImportPower"]

        with pytest.raises(ValidationError):
            Capabilities(**sample_capabilities_data)


class TestDevice:
    """Test the Device model."""

    @pytest.fixture
    def sample_device_data(self):
        """Sample device data."""
        return {
            "id": "test-device-id",
            "givenDisplayName": "Test Device",
            "displayIcon": "TestIcon",
            "settings": [
                {"name": "Power", "value": "True"},
                {"name": "Temperature", "value": "22"},
            ],
            "macAddress": "00:11:22:33:44:55",
            "timeZone": "UTC",
            "rssi": 75,
            "ftcModel": 1,
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
                "ftcModel": 1,
                "refridgerentAddress": 1,
                "hasDemandSideControl": False,
            },
        }

    def test_device_creation(self, sample_device_data):
        """Test creating a device."""
        device = Device(**sample_device_data)

        assert device.id == "test-device-id"
        assert device.given_display_name == "Test Device"
        assert device.device_type is None  # Default value
        assert len(device.settings) == 2
        assert device.is_connected is True

    def test_device_with_device_type(self, sample_device_data):
        """Test device with device_type set."""
        sample_device_data["device_type"] = "atwunit"
        device = Device(**sample_device_data)

        assert device.device_type == "atwunit"

    def test_device_settings_validation(self, sample_device_data):
        """Test that settings are properly validated."""
        device = Device(**sample_device_data)

        assert isinstance(device.settings[0], Setting)
        assert device.settings[0].name == "Power"
        assert device.settings[0].value == "True"

    def test_device_capabilities_validation(self, sample_device_data):
        """Test that capabilities are properly validated."""
        device = Device(**sample_device_data)

        assert isinstance(device.capabilities, Capabilities)
        assert device.capabilities.has_hot_water is True


class TestBuilding:
    """Test the Building model."""

    @pytest.fixture
    def sample_building_data(self):
        """Sample building data."""
        return {
            "id": "building-id",
            "name": "Test Building",
            "timezone": "UTC",
            "airToAirUnits": [],
            "airToWaterUnits": [],
        }

    def test_building_creation(self, sample_building_data):
        """Test creating a building."""
        building = Building(**sample_building_data)

        assert building.id == "building-id"
        assert building.name == "Test Building"
        assert building.timezone == "UTC"
        assert len(building.air_to_air_units) == 0
        assert len(building.air_to_water_units) == 0

    def test_building_with_devices(self, sample_building_data):
        """Test building with devices."""
        device_data = {
            "id": "test-device",
            "givenDisplayName": "Test Device",
            "displayIcon": "Icon",
            "settings": [],
            "macAddress": "00:11:22:33:44:55",
            "timeZone": "UTC",
            "rssi": 75,
            "ftcModel": 1,
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
                "hasDemandSideControl": False,
            },
        }

        sample_building_data["airToWaterUnits"] = [device_data]
        building = Building(**sample_building_data)

        assert len(building.air_to_water_units) == 1
        assert isinstance(building.air_to_water_units[0], Device)


class TestUserProfile:
    """Test the UserProfile model."""

    @pytest.fixture
    def sample_user_profile_data(self):
        """Sample user profile data."""
        return {
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
            "scenes": [],
        }

    def test_user_profile_creation(self, sample_user_profile_data):
        """Test creating a user profile."""
        profile = UserProfile(**sample_user_profile_data)

        assert profile.id == "user-id"
        assert profile.firstname == "Test"
        assert profile.lastname == "User"
        assert profile.email == "test@example.com"
        assert profile.number_of_devices_allowed == 10

    def test_user_profile_field_aliases(self, sample_user_profile_data):
        """Test that field aliases work correctly."""
        profile = UserProfile(**sample_user_profile_data)

        assert (
            profile.number_of_devices_allowed
            == sample_user_profile_data["numberOfDevicesAllowed"]
        )
        assert (
            profile.number_of_buildings_allowed
            == sample_user_profile_data["numberOfBuildingsAllowed"]
        )

    def test_user_profile_with_buildings(self, sample_user_profile_data):
        """Test user profile with buildings."""
        building_data = {
            "id": "building-id",
            "name": "Test Building",
            "timezone": "UTC",
            "airToAirUnits": [],
            "airToWaterUnits": [],
        }

        sample_user_profile_data["buildings"] = [building_data]
        profile = UserProfile(**sample_user_profile_data)

        assert len(profile.buildings) == 1
        assert isinstance(profile.buildings[0], Building)

    def test_user_profile_missing_required_field(self, sample_user_profile_data):
        """Test that missing required fields raise validation error."""
        del sample_user_profile_data["email"]

        with pytest.raises(ValidationError):
            UserProfile(**sample_user_profile_data)
