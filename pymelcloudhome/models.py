"""Legacy models import - now redirects to the new models structure."""

# Import from the new modular structure for backward compatibility
from .models.base import Setting, Capabilities
from .models.device import Device
from .models.building import Building
from .models.user import UserProfile

__all__ = [
    "Setting",
    "Capabilities", 
    "Device",
    "Building",
    "UserProfile",
]
