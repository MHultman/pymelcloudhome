#!/usr/bin/env python3
"""
Device State Example: Get and display device states

This example demonstrates how to:
1. Login and get devices
2. Retrieve current state for each device
3. Display device settings in a readable format
"""

import asyncio
import logging
import os

from pymelcloudhome import MelCloudHomeClient
from pymelcloudhome.errors import ApiError, LoginError

# Set up logging
logging.basicConfig(level=logging.INFO)


async def main():
    """Main example function."""
    email = os.getenv("MELCLOUD_EMAIL")
    password = os.getenv("MELCLOUD_PASSWORD")

    if not email or not password:
        print("Please set MELCLOUD_EMAIL and MELCLOUD_PASSWORD environment variables")
        return

    try:
        async with MelCloudHomeClient() as client:
            await client.login(email, password)
            print("✓ Login successful!")

            devices = await client.list_devices()

            if not devices:
                print("No devices found.")
                return

            for device in devices:
                print(f"\n{'='*60}")
                print(f"Device: {device.given_display_name}")
                print(f"Type: {device.device_type}")
                print(f"{'='*60}")

                # Get current state
                state = await client.get_device_state(device.id)

                if state:
                    print("Current Settings:")
                    for setting_name, setting_value in state.items():
                        print(f"  {setting_name}: {setting_value}")
                else:
                    print("  No state information available")

                # Display capabilities
                print("\nCapabilities:")
                caps = device.capabilities
                print(
                    f"  Temperature Range: {caps.min_set_temperature}°C - {caps.max_set_temperature}°C"
                )
                print(f"  Hot Water: {'Yes' if caps.has_hot_water else 'No'}")
                print(f"  Zone 2: {'Yes' if caps.has_zone2 else 'No'}")
                print(f"  Half Degrees: {'Yes' if caps.has_half_degrees else 'No'}")

                if caps.has_hot_water:
                    print(
                        f"  Tank Temperature Range: {caps.min_set_tank_temperature}°C - {caps.max_set_tank_temperature}°C"
                    )

    except LoginError as e:
        print(f"❌ Login failed: {e}")
    except ApiError as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
