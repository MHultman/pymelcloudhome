#!/usr/bin/env python3
"""
Control ATW Example: Control an Air-to-Water heat pump

This example demonstrates how to:
1. Find ATW (Air-to-Water) devices
2. Control power, temperature, and hot water settings
3. Handle errors gracefully

Note: This example only works if you have ATW devices in your account.
"""

import asyncio
import logging
import os
from pymelcloudhome import MelCloudHomeClient
from pymelcloudhome.errors import LoginError, ApiError, DeviceNotFound

# Set up logging
logging.basicConfig(level=logging.INFO)

async def control_atw_device(client: MelCloudHomeClient, device):
    """Demonstrate controlling an ATW device."""
    print(f"\nControlling ATW device: {device.given_display_name}")
    print(f"Device ID: {device.id}")
    
    try:
        # Get current state
        current_state = await client.get_device_state(device.id)
        if current_state:
            print(f"Current Power: {current_state.get('Power', 'Unknown')}")
            print(f"Current Zone 1 Temperature: {current_state.get('SetTemperatureZone1', 'Unknown')}")
            print(f"Current Tank Temperature: {current_state.get('SetTankWaterTemperature', 'Unknown')}")
        
        # Example 1: Turn on the device and set temperature
        print("\n🔧 Setting device to ON with Zone 1 temperature to 22°C...")
        response = await client.set_device_state(
            device.id, 
            device.device_type, 
            {
                "power": True,
                "setTemperatureZone1": 22.0
            }
        )
        print(f"✓ Response: {response}")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Example 2: Set hot water temperature (if supported)
        if device.capabilities.has_hot_water:
            print("\n🔧 Setting hot water temperature to 55°C...")
            response = await client.set_device_state(
                device.id,
                device.device_type,
                {
                    "setTankWaterTemperature": 55
                }
            )
            print(f"✓ Response: {response}")
        else:
            print("\nℹ️  Device does not support hot water control")
        
        # Example 3: Enable forced hot water mode (if supported)
        if device.capabilities.has_hot_water:
            print("\n🔧 Enabling forced hot water mode...")
            response = await client.set_device_state(
                device.id,
                device.device_type,
                {
                    "forcedHotWaterMode": True
                }
            )
            print(f"✓ Response: {response}")
            
            # Wait and then disable it
            await asyncio.sleep(5)
            print("\n🔧 Disabling forced hot water mode...")
            response = await client.set_device_state(
                device.id,
                device.device_type,
                {
                    "forcedHotWaterMode": False
                }
            )
            print(f"✓ Response: {response}")
        
    except DeviceNotFound as e:
        print(f"❌ Device not found: {e}")
    except ApiError as e:
        print(f"❌ API error when controlling device: {e}")

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
            
            # Find ATW devices
            atw_devices = [d for d in devices if d.device_type == "atwunit"]
            
            if not atw_devices:
                print("❌ No ATW (Air-to-Water) devices found.")
                print("This example requires ATW devices to demonstrate control.")
                return
            
            print(f"Found {len(atw_devices)} ATW device(s)")
            
            # Control the first ATW device
            await control_atw_device(client, atw_devices[0])
            
            print("\n✓ Example completed successfully!")
            print("Note: Changes may take a few minutes to be reflected in the MelCloud app.")
            
    except LoginError as e:
        print(f"❌ Login failed: {e}")
    except ApiError as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())