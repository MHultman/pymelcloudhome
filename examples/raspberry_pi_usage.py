"""Example usage on Raspberry Pi / ARM64 systems."""

import asyncio
import os

from pymelcloudhome import MelCloudHomeClient


async def main():
    """Example of using pymelcloudhome on Raspberry Pi or ARM64 systems."""

    # On ARM64/Raspberry Pi, you MUST provide the system Chromium path
    # because pyppeteer's bundled Chromium doesn't support ARM architecture

    # Common paths:
    # - Debian/Ubuntu/Raspberry Pi OS: /usr/bin/chromium-browser
    # - Alpine Linux (Docker): /usr/bin/chromium
    # - macOS ARM: /Applications/Chromium.app/Contents/MacOS/Chromium

    chromium_path = "/usr/bin/chromium-browser"

    # You can also detect the system and choose the appropriate path:
    # import platform
    # if platform.machine() in ['aarch64', 'armv7l']:  # ARM64 or ARM32
    #     chromium_path = "/usr/bin/chromium-browser"
    # elif platform.system() == 'Darwin' and platform.machine() == 'arm64':  # macOS ARM
    #     chromium_path = "/Applications/Chromium.app/Contents/MacOS/Chromium"

    email = os.environ.get("MELCLOUD_EMAIL", "your-email@example.com")
    password = os.environ.get("MELCLOUD_PASSWORD", "your-password")

    print(f"Using Chromium at: {chromium_path}")

    async with MelCloudHomeClient(chromium_executable_path=chromium_path) as client:
        print("Logging in...")
        await client.login(email, password)
        print("Login successful!")

        print("\nFetching devices...")
        devices = await client.list_devices()

        print(f"\nFound {len(devices)} device(s):\n")
        for device in devices:
            print(f"Device: {device.given_display_name}")
            print(f"  ID: {device.id}")
            print(f"  Type: {device.device_type}")
            print(f"  Connected: {device.is_connected}")
            print(f"  Settings: {len(device.settings)} settings")
            print()


if __name__ == "__main__":
    asyncio.run(main())
