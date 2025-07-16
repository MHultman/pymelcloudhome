
# pymelcloudhome

A modern, fully asynchronous Python library for the Mitsubishi Electric "MelCloudHome" platform API.

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
