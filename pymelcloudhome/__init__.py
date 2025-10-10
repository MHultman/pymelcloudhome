"""A modern, fully asynchronous Python library for the Mitsubishi Electric MelCloudHome platform."""

from .client import MelCloudHomeClient
from . import models
from . import errors

__version__ = "0.1.1"
__all__ = ["MelCloudHomeClient", "models", "errors", "__version__"]
