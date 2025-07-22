
# pymelcloudhome

A modern, fully asynchronous Python library for the Mitsubishi Electric "MelCloudHome" platform API, with persistent session handling.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [`login(email: str, password: str)`](#loginemail-str-password-str)
  - [`list_devices() -> List[Device]`](#list_devices---listdevice)
  - [`get_device_state(device_id: str) -> Optional[Dict[str, Any]]`](#get_device_statedevice_id-str---optionaldictstr-any)
  - [`set_device_state(device_id: str, device_type: str, state_data: dict) -> dict`](#set_device_statedevice_id-str-device_type-str-state_data-dict---dict)
  - [`close()`](#close)
  - [Caching](#caching)
- [Automatic Session Renewal](#automatic-session-renewal)
- [Error Handling](#error-handling)
  - [Example of Handling Errors](#example-of-handling-errors)
- [Example Usage](#example-usage)
- [Running Tests](#running-tests)
- [Contributing](#contributing)

## Installation

For developers working on `pymelcloudhome`, you'll need [Poetry](https://python-poetry.org/docs/#installation) to manage dependencies.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/pymelcloudhome.git
    cd pymelcloudhome
    ```

2.  **Install all dependencies (production and development):**

    ```bash
    poetry install
    ```

This command will create a virtual environment and install all necessary packages, including those required for testing, linting, and type checking.

If you are a user and only want to install the library as a dependency in your project, you can use pip:

```bash
pip install pymelcloudhome
```

## Usage

The `MelCloudHomeClient` provides the following asynchronous methods to interact with the MelCloud Home API:

### `login(email: str, password: str)`
Logs in to the MelCloud Home platform. This method uses a headless browser (Playwright) to handle the login process, including any JavaScript-based authentication.

```python
await client.login("your-email@example.com", "your-password")
```

### `list_devices() -> List[Device]`
Retrieves a list of all devices associated with the logged-in user. Each `Device` object contains details about the unit, including its type (`ataunit` for Air-to-Air or `atwunit` for Air-to-Water) and current settings.

```python
devices = await client.list_devices()
for device in devices:
    print(f"Device ID: {device.id}, Name: {device.given_display_name}, Type: {device.device_type}")
```

### `get_device_state(device_id: str) -> Optional[Dict[str, Any]]`
Retrieves the current operational state of a specific device from the cached data. This method does not make a new API call. It returns a dictionary of the device's settings or `None` if the device is not found.

```python
device_id = "your-device-id" # e.g., "d3c4b5a6-f7e8-9012-cbad-876543210fed"
state = await client.get_device_state(device_id)
if state:
    print(f"Device state: {state}")
```

### `set_device_state(device_id: str, device_type: str, state_data: dict) -> dict`
Updates the operational state of a specific device.
- `device_id`: The ID of the device to update.
- `device_type`: The type of the device, either "ataunit" or "atwunit".
- `state_data`: A dictionary containing the settings to update and their new values.

For ATW (Air-to-Water) devices, common `state_data` values you might send include:
- `"power"`: `True` or `False` (to turn the device on or off)
- `"setTemperatureZone1"`: A float representing the target temperature for Zone 1 (e.g., `22.0`)
- Other values may be available depending on your specific device model and its capabilities. You can inspect the output of `get_device_state` to discover more controllable parameters.

```python
device_id = "your-device-id"
device_type = "atwunit" # or "ataunit"
new_state = {"power": True, "setTemperatureZone1": 23.5}
response = await client.set_device_state(device_id, device_type, new_state)
print(f"Set device state response: {response}")
```

### `close()`
Closes the underlying aiohttp client session. This method is automatically called when using the client as an asynchronous context manager (`async with`).

```python
await client.close()
```

### Caching

To minimize API calls and improve performance, the `MelCloudHomeClient` caches the user profile data. By default, this cache lasts for 5 minutes. You can configure this duration by passing the `cache_duration_minutes` parameter when creating the client.

```python
# Use a 10-minute cache
client = MelCloudHomeClient(cache_duration_minutes=10)
```

This means that subsequent calls to `list_devices()` and `get_device_state()` within this timeframe will use the cached data instead of making a new API request to fetch the user context.

## Automatic Session Renewal

The client is designed to be resilient to session expiry. If an API call fails with a `401 Unauthorized` status, the library will automatically attempt to re-authenticate using the credentials you provided during the initial `login` call. If the re-login is successful, the original request will be retried automatically.

This makes the client more robust for long-running applications, as you do not need to manually handle session expiry.

## Error Handling

The library uses custom exceptions to indicate specific types of failures. It is best practice to wrap your client calls in a `try...except` block to handle these potential errors gracefully.

There are three main exceptions you should be prepared to handle:

- **`LoginError`**: Raised when the initial authentication with MELCloud fails. This is typically caused by incorrect credentials (email or password) or a change in the MELCloud login page. It does not contain an HTTP status code, as it originates from the browser automation process.

- **`ApiError`**: Raised for any failed API call that does not resolve after a potential re-login attempt. This can happen if the API endpoint is not found, the server returns an error, or if a re-login attempt also fails. This exception contains a `.status` attribute with the HTTP status code (e.g., `404`, `500`) and a `.message` attribute with the error details from the server.

- **`DeviceNotFound`**: Raised when an operation is attempted on a device that does not exist or is not properly configured.

### Example of Handling Errors

```python
import asyncio
from pymelcloudhome import MelCloudHomeClient
from pymelcloudhome.errors import LoginError, ApiError, DeviceNotFound

async def main():
    async with MelCloudHomeClient() as client:
        try:
            # Attempt to log in
            await client.login("your-email@example.com", "your-password")
            print("Login successful!")

            # Perform operations
            devices = await client.list_devices()
            if not devices:
                print("No devices found.")
                return

            # ... your code to interact with devices ...

        except LoginError:
            print("Login failed. Please check your email and password.")
        except ApiError as e:
            print(f"An API error occurred: Status {e.status} - {e.message}")
        except DeviceNotFound:
            print("The specified device could not be found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Example Usage

```python
import asyncio
from pymelcloudhome import MelCloudHomeClient

async def main():
    async with MelCloudHomeClient() as client:
        await client.login("your-email@example.com", "your-password")

        # List all devices
        devices = await client.list_devices()
        print("Discovered Devices:")
        for device in devices:
            print(f"  - ID: {device.id}, Name: {device.given_display_name}, Type: {device.device_type}")

        if devices:
            # Get state of the first device
            first_device_id = devices[0].id
            current_state = await client.get_device_state(first_device_id)
            print(f"Current state of {devices[0].given_display_name}: {current_state}")

            # Example: Set power and temperature for an ATW unit
            if devices[0].device_type == "atwunit":
                print(f"Attempting to set state for ATW unit: {devices[0].given_display_name}")
                update_data = {"power": True, "setTemperatureZone1": 22.0}
                set_response = await client.set_device_state(first_device_id, "atwunit", update_data)
                print(f"Set state response: {set_response}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Running Tests

To run the test suite, first install the development dependencies:

```bash
poetry install
```

Then, run pytest:

```bash
poetry run pytest
```

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting a pull request.
