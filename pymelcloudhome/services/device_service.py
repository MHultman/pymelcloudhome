"""Device operations service."""

import logging
from typing import Any, Dict, List, Optional

from ..config import DEVICE_TYPE_AIR_TO_AIR, DEVICE_TYPE_AIR_TO_WATER
from ..errors import DeviceNotFound, LoginError
from ..models import Device, UserProfile
from .api_client import ApiClient

logger = logging.getLogger(__name__)


class DeviceService:
    """Handles device-related operations."""

    def __init__(self, api_client: ApiClient):
        """Initialize the device service."""
        self._api_client = api_client

    def extract_devices_from_profile(self, user_profile: UserProfile) -> List[Device]:
        """
        Extract all devices from user profile.
        
        Args:
            user_profile: The user profile containing buildings and devices
            
        Returns:
            List of all devices with their types set
        """
        devices = []
        
        for building in user_profile.buildings:
            devices.extend(self._extract_air_to_air_units(building.air_to_air_units))
            devices.extend(self._extract_air_to_water_units(building.air_to_water_units))
        
        logger.debug("Extracted %d devices from user profile", len(devices))
        return devices

    def _extract_air_to_air_units(self, units: List[Device]) -> List[Device]:
        """Extract air-to-air units and set their device type."""
        for unit in units:
            unit.device_type = DEVICE_TYPE_AIR_TO_AIR
        return units

    def _extract_air_to_water_units(self, units: List[Device]) -> List[Device]:
        """Extract air-to-water units and set their device type."""
        for unit in units:
            unit.device_type = DEVICE_TYPE_AIR_TO_WATER
        return units

    def find_device_by_id(self, user_profile: UserProfile, device_id: str) -> Optional[Device]:
        """
        Find a specific device by ID in the user profile.
        
        Args:
            user_profile: The user profile to search in
            device_id: ID of the device to find
            
        Returns:
            The device if found, None otherwise
        """
        all_devices = self._get_all_devices_from_profile(user_profile)
        
        for device in all_devices:
            if device.id == device_id:
                return device
        
        logger.warning("Device with ID %s not found", device_id)
        return None

    def extract_device_state(self, device: Device) -> Dict[str, Any]:
        """
        Extract device state as a dictionary.
        
        Args:
            device: The device to extract state from
            
        Returns:
            Dictionary mapping setting names to values
        """
        return {setting.name: setting.value for setting in device.settings}

    def get_device_state_by_id(
        self, 
        user_profile: Optional[UserProfile], 
        device_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get device state by device ID.
        
        Args:
            user_profile: The user profile (must not be None)
            device_id: ID of the device
            
        Returns:
            Device state dictionary or None if not found
            
        Raises:
            LoginError: If user profile is not available
        """
        if not user_profile:
            raise LoginError("User profile is not available.")

        device = self.find_device_by_id(user_profile, device_id)
        if device:
            return self.extract_device_state(device)
        
        return None

    async def update_device_state(
        self, 
        device_id: str, 
        device_type: str, 
        state_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update device state via API.
        
        Args:
            device_id: ID of the device to update
            device_type: Type of device (ataunit or atwunit)
            state_data: New state data to apply
            
        Returns:
            API response
            
        Raises:
            DeviceNotFound: If device type is not set
        """
        if not device_type:
            raise DeviceNotFound("Device type is not set for this device.")

        api_endpoint = f"{device_type}/{device_id}"
        logger.info("Updating device %s state", device_id)
        
        return await self._api_client.make_request(
            "put", 
            api_endpoint, 
            json=state_data
        )

    def _get_all_devices_from_profile(self, user_profile: UserProfile) -> List[Device]:
        """Get all devices from all buildings in the profile."""
        all_devices = []
        for building in user_profile.buildings:
            all_devices.extend(building.air_to_air_units)
            all_devices.extend(building.air_to_water_units)
        return all_devices