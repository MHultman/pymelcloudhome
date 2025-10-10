#!/usr/bin/env python3
"""
Basic Example: Login and list devices

This example demonstrates how to:
1. Create a client
2. Login to MelCloudHome
3. List all available devices
4. Display basic device information
"""

import asyncio
import logging
import os
from pymelcloudhome import MelCloudHomeClient
from pymelcloudhome.errors import LoginError, ApiError

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def main():
    """Main example function."""
    # Get credentials from environment variables
    email = os.getenv("MELCLOUD_EMAIL")
    password = os.getenv("MELCLOUD_PASSWORD")
    
    if not email or not password:
        print("Please set MELCLOUD_EMAIL and MELCLOUD_PASSWORD environment variables")
        print("Example:")
        print("export MELCLOUD_EMAIL=your-email@example.com")
        print("export MELCLOUD_PASSWORD=your-password")
        return
    
    try:
        async with MelCloudHomeClient() as client:
            # Login
            print(f"Logging in as {email}...")
            await client.login(email, password)
            print("✓ Login successful!")
            
            # List devices
            print("\nDiscovering devices...")
            devices = await client.list_devices()
            
            if not devices:
                print("No devices found.")
                return
            
            print(f"Found {len(devices)} device(s):")
            print("-" * 60)
            
            for i, device in enumerate(devices, 1):
                print(f"{i}. {device.given_display_name}")
                print(f"   ID: {device.id}")
                print(f"   Type: {device.device_type}")
                print(f"   MAC: {device.mac_address}")
                print(f"   Connected: {'Yes' if device.is_connected else 'No'}")
                print(f"   Error: {'Yes' if device.is_in_error else 'No'}")
                print()
                
    except LoginError as e:
        print(f"❌ Login failed: {e}")
    except ApiError as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())