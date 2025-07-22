import pytest
from aiohttp import web

from pymelcloudhome.client import MelCloudHomeClient
from pymelcloudhome.errors import ApiError, DeviceNotFound


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
                "buildings": [],
                "guestBuildings": [],
                "scenes": [],
            }
        )

    async def error_handler(request):
        return web.Response(text="Internal Server Error", status=500)

    app.router.add_get("/user/context", context_handler)
    app.router.add_put("/ataunit/1234", error_handler)

    return await aiohttp_client(app)


@pytest.fixture
async def api_error_client(aiohttp_client):
    """Fixture for a client that always returns an API error."""
    app = web.Application()

    async def error_handler(request):
        return web.Response(text="Internal Server Error", status=500)

    app.router.add_get("/user/context", error_handler)

    return await aiohttp_client(app)


async def test_login_error(api_error_client):
    """Test that an ApiError is raised when login fails."""
    melcloud_client = MelCloudHomeClient(session=api_error_client.session)
    melcloud_client._session._base_url = api_error_client.server.make_url("/")

    with pytest.raises(ApiError):
        await melcloud_client.list_devices()


async def test_api_error(api_error_client):
    """Test that an ApiError is raised on API failure."""
    melcloud_client = MelCloudHomeClient(session=api_error_client.session)
    melcloud_client._session._base_url = api_error_client.server.make_url("/")

    with pytest.raises(ApiError) as excinfo:
        await melcloud_client._fetch_context()

    assert excinfo.value.status == 500


async def test_device_not_found_error(client):
    """Test that a DeviceNotFound is raised for a device with no type."""
    melcloud_client = MelCloudHomeClient(session=client.session)
    melcloud_client._session._base_url = client.server.make_url("/")
    await melcloud_client._fetch_context()

    with pytest.raises(DeviceNotFound):
        await melcloud_client.set_device_state("1234", "", {})


async def test_set_device_state_api_error(client):
    """Test that an ApiError is raised on set_device_state failure."""
    melcloud_client = MelCloudHomeClient(session=client.session)
    melcloud_client._session._base_url = client.server.make_url("/")
    await melcloud_client._fetch_context()

    with pytest.raises(ApiError) as excinfo:
        await melcloud_client.set_device_state("1234", "ataunit", {})

    assert excinfo.value.status == 500
