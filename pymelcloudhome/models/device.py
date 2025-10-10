"""Device model."""

from typing import List, Optional

from pydantic import BaseModel, Field

from .base import Setting, Capabilities


class Device(BaseModel):
    """Represents a MELCloud Home device (air-to-air or air-to-water unit)."""
    id: str
    device_type: Optional[str] = None  # 'atwunit' or 'ataunit'
    given_display_name: str = Field(..., alias="givenDisplayName")
    display_icon: str = Field(..., alias="displayIcon")
    settings: List[Setting]
    mac_address: str = Field(..., alias="macAddress")
    time_zone: str = Field(..., alias="timeZone")
    rssi: int
    ftc_model: int = Field(..., alias="ftcModel")
    schedule: List
    schedule_enabled: bool = Field(..., alias="scheduleEnabled")
    frost_protection: Optional[str] = Field(..., alias="frostProtection")
    overheat_protection: Optional[str] = Field(..., alias="overheatProtection")
    holiday_mode: Optional[str] = Field(..., alias="holidayMode")
    is_connected: bool = Field(..., alias="isConnected")
    is_in_error: bool = Field(..., alias="isInError")
    capabilities: Capabilities