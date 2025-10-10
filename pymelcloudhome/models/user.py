"""User profile model."""


from pydantic import BaseModel, Field

from .building import Building


class UserProfile(BaseModel):
    """Represents a user profile with associated buildings and devices."""

    id: str
    firstname: str
    lastname: str
    email: str
    language: str
    number_of_devices_allowed: int = Field(..., alias="numberOfDevicesAllowed")
    number_of_buildings_allowed: int = Field(..., alias="numberOfBuildingsAllowed")
    number_of_guest_users_allowed_per_unit: int = Field(
        ..., alias="numberOfGuestUsersAllowedPerUnit"
    )
    number_of_guest_devices_allowed: int = Field(
        ..., alias="numberOfGuestDevicesAllowed"
    )
    buildings: list[Building]
    guest_buildings: list = Field(..., alias="guestBuildings")
    scenes: list
