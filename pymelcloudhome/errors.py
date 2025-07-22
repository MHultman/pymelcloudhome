"""Custom exceptions for pymelcloudhome."""


class MelCloudHomeError(Exception):
    """Base exception for pymelcloudhome."""


class LoginError(MelCloudHomeError):
    """Raised when login fails."""


class ApiError(MelCloudHomeError):
    """Raised when an API call fails."""

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"API request failed with status {status}: {message}")


class DeviceNotFound(MelCloudHomeError):
    """Raised when a device is not found."""
