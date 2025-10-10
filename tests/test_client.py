import pytest
from aiohttp import web

from pymelcloudhome.client import MelCloudHomeClient


@pytest.fixture
async def client(aiohttp_client):
    """Fixture for creating a MelCloudHomeClient with a mock server."""
    app = web.Application()

    async def context_handler(request):
        return web.json_response(
            {
                "id": "f1e2d3c4-b5a6-7890-fedc-ba9876543210",
                "firstname": "First Name",
                "lastname": "Last Name",
                "email": "email@domain.xxx",
                "language": "sv",
                "numberOfDevicesAllowed": 10,
                "numberOfBuildingsAllowed": 2,
                "numberOfGuestUsersAllowedPerUnit": 5,
                "numberOfGuestDevicesAllowed": 10,
                "buildings": [
                    {
                        "id": "e2d3c4b5-a6f7-8901-dcba-9876543210fe",
                        "name": "Address name number",
                        "timezone": "Europe/Berlin",
                        "airToAirUnits": [],
                        "airToWaterUnits": [
                            {
                                "id": "d3c4b5a6-f7e8-9012-cbad-876543210fed",
                                "givenDisplayName": "Värmepanna",
                                "displayIcon": "Loft",
                                "settings": [
                                    {"name": "Power", "value": "True"},
                                    {"name": "InStandbyMode", "value": "False"},
                                ],
                                "macAddress": "282e89465b95",
                                "timeZone": "Europe/Berlin",
                                "rssi": 0,
                                "ftcModel": 5,
                                "schedule": [],
                                "scheduleEnabled": True,
                                "frostProtection": None,
                                "overheatProtection": None,
                                "holidayMode": None,
                                "isConnected": True,
                                "isInError": False,
                                "capabilities": {
                                    "maxImportPower": 0,
                                    "maxHeatOutput": 0,
                                    "temperatureUnit": "",
                                    "hasHotWater": False,
                                    "immersionHeaterCapacity": 0,
                                    "minSetTankTemperature": 0,
                                    "maxSetTankTemperature": 0,
                                    "minSetTemperature": 20,
                                    "maxSetTemperature": 50,
                                    "temperatureIncrement": 0,
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
                                    "hasEstimatedEnergyConsumption": True,
                                    "hasEstimatedEnergyProduction": True,
                                    "ftcModel": 0,
                                    "refridgerentAddress": 0,
                                    "hasDemandSideControl": False,
                                },
                            }
                        ],
                    }
                ],
                "guestBuildings": [],
                "scenes": [],
            }
        )

    async def set_state_handler(request):
        return web.json_response({"status": "ok"})

    app.router.add_get("/user/context", context_handler)
    app.router.add_put(
        "/atwunit/d3c4b5a6-f7e8-9012-cbad-876543210fed", set_state_handler
    )

    return await aiohttp_client(app)


async def test_list_devices(client):
    """Test listing devices."""
    melcloud_client = MelCloudHomeClient(session=client.session)
    melcloud_client._session._base_url = client.server.make_url("/")
    # Use the new internal method to refresh user profile
    await melcloud_client._refresh_user_profile()

    devices = await melcloud_client.list_devices()

    assert len(devices) == 1
    assert devices[0].id == "d3c4b5a6-f7e8-9012-cbad-876543210fed"


async def test_get_device_state(client):
    """Test getting device state."""
    melcloud_client = MelCloudHomeClient(session=client.session)
    melcloud_client._session._base_url = client.server.make_url("/")
    await melcloud_client._refresh_user_profile()

    state = await melcloud_client.get_device_state(
        "d3c4b5a6-f7e8-9012-cbad-876543210fed"
    )

    assert state is not None
    assert state["Power"] == "True"
    assert state["InStandbyMode"] == "False"


async def test_set_device_state(client):
    """Test setting device state."""
    melcloud_client = MelCloudHomeClient(session=client.session)
    melcloud_client._session._base_url = client.server.make_url("/")
    await melcloud_client._refresh_user_profile()

    # First, list devices to get the device_type
    devices = await melcloud_client.list_devices()
    device = devices[0]

    # Ensure device_type is set (it should be from the device service)
    assert device.device_type is not None
    
    response = await melcloud_client.set_device_state(
        device.id, device.device_type, {"Power": "False"}
    )

    assert response is not None
