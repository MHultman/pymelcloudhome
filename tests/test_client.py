
import asyncio
from datetime import datetime

import pytest
from aiohttp import web, ClientSession

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

    app.router.add_get("/user/context", context_handler)

    return await aiohttp_client(app)


async def test_list_devices(client):
    """Test listing devices."""
    melcloud_client = MelCloudHomeClient(session=client.session)
    melcloud_client._session._base_url = client.server.make_url('/')
    melcloud_client._user_profile = None
    melcloud_client._last_updated = None

    devices = await melcloud_client.list_devices()

    print (devices)  # For debugging purposes

    assert len(devices) == 1
    assert devices[0].id == "d3c4b5a6-f7e8-9012-cbad-876543210fed"
