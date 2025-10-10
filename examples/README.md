# Examples

This directory contains practical examples demonstrating how to use the `pymelcloudhome` library.

## Setting up credentials

All examples require MelCloudHome credentials. Set them as environment variables:

```bash
export MELCLOUD_EMAIL="your-email@example.com"
export MELCLOUD_PASSWORD="your-password"
```

On Windows (PowerShell):

```powershell
$env:MELCLOUD_EMAIL="your-email@example.com"
$env:MELCLOUD_PASSWORD="your-password"
```

Alternatively, create a `.env` file in the project root:

```
MELCLOUD_EMAIL=your-email@example.com
MELCLOUD_PASSWORD=your-password
```

## Examples

### 1. `basic_usage.py`

The simplest example showing how to login and list devices.

```bash
python examples/basic_usage.py
```

### 2. `device_state.py`

Shows how to retrieve and display the current state of all devices, including their settings and capabilities.

```bash
python examples/device_state.py
```

### 3. `control_atw.py`

Demonstrates controlling Air-to-Water (ATW) heat pump devices. This includes:

- Setting power state
- Adjusting temperature settings
- Controlling hot water temperature
- Enabling/disabling forced hot water mode

```bash
python examples/control_atw.py
```

**Note:** The control example only works if you have ATW devices in your account.

## Running Examples

Make sure you have installed the package and its dependencies:

```bash
poetry install
```

Then run any example:

```bash
poetry run python examples/basic_usage.py
```

## Safety Note

The control examples will make actual changes to your devices. Use them carefully and ensure you understand what each command does before running it.
