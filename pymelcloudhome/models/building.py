"""Building model."""


from pydantic import BaseModel, Field

from .device import Device


class Building(BaseModel):
    """Represents a building containing devices."""

    id: str
    name: str
    timezone: str
    air_to_air_units: list[Device] = Field(..., alias="airToAirUnits")
    air_to_water_units: list[Device] = Field(..., alias="airToWaterUnits")
