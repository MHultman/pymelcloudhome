import os
import pytest
from dotenv import load_dotenv
from pymelcloudhome.client import MelCloudHomeClient

load_dotenv()


@pytest.mark.skipif(
    not os.environ.get("MELCLOUD_EMAIL") or not os.environ.get("MELCLOUD_PASSWORD"),
    reason="MELCLOUD_EMAIL and MELCLOUD_PASSWORD environment variables not set.",
)
@pytest.mark.asyncio
async def test_real_login():
    """Tests the real login functionality with user credentials."""
    email = os.environ.get("MELCLOUD_EMAIL")
    password = os.environ.get("MELCLOUD_PASSWORD")

    async with MelCloudHomeClient() as client:
        await client.login(email, password)

        devices = await client.list_devices()
        print("\nDevice Configurations:")
        print(devices)

        assert devices, "Device list is empty after login."
