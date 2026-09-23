from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)

class EnvironmentalCreate(BaseModel):
    date: str
    location: str = Field(min_length=2, max_length=80)
    temperature_c: float
    humidity_pct: float = Field(ge=0, le=100)
    rainfall_mm: float = Field(ge=0)
    co2_ppm: float = Field(gt=0)
    aqi: float = Field(ge=0, le=500)
    energy_kwh: float = Field(ge=0)
    water_liters: float = Field(ge=0)
    renewable_pct: float = Field(ge=0, le=100)
    extreme_weather_index: float = Field(ge=0, le=100)

class PredictionInput(BaseModel):
    temperature_c: float
    humidity_pct: float
    rainfall_mm: float
    co2_ppm: float
    aqi: float
    water_liters: float
    renewable_pct: float
    extreme_weather_index: float
