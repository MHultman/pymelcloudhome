
# pymelcloudhome

A modern, fully asynchronous Python library for the Mitsubishi Electric "MelCloudHome" platform API.

## Installation

```bash
pip install pymelcloudhome
```

## Quick Start

```python
import asyncio
from pymelcloudhome import MelCloudHomeClient

async def main():
    async with MelCloudHomeClient() as client:
        await client.login("your-email@example.com", "your-password")
        devices = await client.list_devices()
        print(devices)

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
