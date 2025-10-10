"""Base model components."""

from pydantic import BaseModel, Field


class Setting(BaseModel):
    """Represents a device setting with name and value."""

    name: str
    value: str


class Capabilities(BaseModel):
    """Device capabilities and limits."""

    max_import_power: int = Field(..., alias="maxImportPower")
    max_heat_output: int = Field(..., alias="maxHeatOutput")
    temperature_unit: str = Field(..., alias="temperatureUnit")
    has_hot_water: bool = Field(..., alias="hasHotWater")
    immersion_heater_capacity: int = Field(..., alias="immersionHeaterCapacity")
    min_set_tank_temperature: int = Field(..., alias="minSetTankTemperature")
    max_set_tank_temperature: int = Field(..., alias="maxSetTankTemperature")
    min_set_temperature: int = Field(..., alias="minSetTemperature")
    max_set_temperature: int = Field(..., alias="maxSetTemperature")
    temperature_increment: float = Field(..., alias="temperatureIncrement")
    temperature_increment_override: str = Field(
        ..., alias="temperatureIncrementOverride"
    )
    has_half_degrees: bool = Field(..., alias="hasHalfDegrees")
    has_zone2: bool = Field(..., alias="hasZone2")
    has_dual_room_temperature: bool = Field(..., alias="hasDualRoomTemperature")
    has_thermostat_zone1: bool = Field(..., alias="hasThermostatZone1")
    has_thermostat_zone2: bool = Field(..., alias="hasThermostatZone2")
    has_heat_zone1: bool = Field(..., alias="hasHeatZone1")
    has_heat_zone2: bool = Field(..., alias="hasHeatZone2")
    has_measured_energy_consumption: bool = Field(
        ..., alias="hasMeasuredEnergyConsumption"
    )
    has_measured_energy_production: bool = Field(
        ..., alias="hasMeasuredEnergyProduction"
    )
    has_estimated_energy_consumption: bool = Field(
        ..., alias="hasEstimatedEnergyConsumption"
    )
    has_estimated_energy_production: bool = Field(
        ..., alias="hasEstimatedEnergyProduction"
    )
    ftc_model: int = Field(..., alias="ftcModel")
    refrigerant_address: int = Field(..., alias="refridgerentAddress")
    has_demand_side_control: bool = Field(..., alias="hasDemandSideControl")
