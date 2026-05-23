import os
import json
from typing import Any
from dataclasses import dataclass

import httpx
from fastmcp import FastMCP

mcp = FastMCP("weather-mcp")

OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5"


@dataclass
class WeatherConfig:
    api_key: str
    units: str = "metric"


def get_config() -> WeatherConfig:
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY environment variable is required")
    return WeatherConfig(api_key=api_key)


async def _get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    config = get_config()
    params = params or {}
    params["appid"] = config.api_key
    params["units"] = config.units
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{OPENWEATHER_BASE}/{path}", params=params)
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def get_weather(city: str) -> str:
    """Get current weather for a city.

    Args:
        city: City name (e.g. "Tokyo,JP" or "London,UK")
    """
    data = await _get("weather", {"q": city})
    return _format_current(data)


@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city.

    Args:
        city: City name (e.g. "Tokyo,JP" or "London,UK")
        days: Number of days (1-5, default 3)
    """
    data = await _get("forecast", {"q": city})
    return _format_forecast(data, days=days)


def _format_current(data: dict[str, Any]) -> str:
    main = data["main"]
    weather = data["weather"][0]
    wind = data.get("wind", {})

    lines = [
        f"Weather in {data['name']}, {data.get('sys', {}).get('country', '')}:",
        f"  {weather['description'].title()}",
        f"  Temperature: {main['temp']}°C (feels like {main['feels_like']}°C)",
        f"  Humidity: {main['humidity']}%",
        f"  Pressure: {main['pressure']} hPa",
        f"  Wind: {wind.get('speed', 'N/A')} m/s",
    ]
    return "\n".join(lines)


def _format_forecast(data: dict[str, Any], days: int = 3) -> str:
    city = data["city"]
    intervals = data["list"]
    intervals_per_day = 8
    total = min(days * intervals_per_day, len(intervals))

    lines = [
        f"Forecast for {city['name']}, {city.get('country', '')} "
        f"({days} day{'s' if days > 1 else ''}):"
    ]

    for i in range(0, total, intervals_per_day):
        day_data = intervals[i]
        main = day_data["main"]
        weather = day_data["weather"][0]
        dt = day_data["dt_txt"]

        lines.append(f"\n  {dt}:")
        lines.append(f"    {weather['description'].title()}")
        lines.append(f"    {main['temp']}°C (high {main['temp_max']}°C / low {main['temp_min']}°C)")

    return "\n".join(lines)


import sys

def main() -> None:
    if "--gui" in sys.argv:
        mcp.gui()
    else:
        mcp.run(transport="http", host="0.0.0.0")


if __name__ == "__main__":
    main()
