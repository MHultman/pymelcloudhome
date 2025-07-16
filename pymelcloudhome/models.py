from typing import List, Optional

from pydantic import BaseModel, Field


class Setting(BaseModel):
    name: str
    value: str


class Capabilities(BaseModel):
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
    refridgerent_address: int = Field(..., alias="refridgerentAddress")
    has_demand_side_control: bool = Field(..., alias="hasDemandSideControl")


class Device(BaseModel):
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


class Building(BaseModel):
    id: str
    name: str
    timezone: str
    air_to_air_units: List[Device] = Field(..., alias="airToAirUnits")
    air_to_water_units: List[Device] = Field(..., alias="airToWaterUnits")


class UserProfile(BaseModel):
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
    buildings: List[Building]
    guest_buildings: List = Field(..., alias="guestBuildings")
    scenes: List
