"""OpenWeather MCP Server implementation using the FastMCP framework."""

import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP
import httpx

# Load environment variables from a local .env file if present
load_dotenv()

# Initialize the FastMCP server instance
mcp = FastMCP("weather-mcp")

# OpenWeatherMap API v2.5 base endpoint URL
OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5"


@dataclass
class WeatherConfig:
    """Configuration class for weather API authentication and preferences."""

    api_key: str
    units: str = "metric"  # Default to metric units (Celsius, m/s)


def get_config() -> WeatherConfig:
    """Retrieve weather configuration from environment variables.

    Returns:
        WeatherConfig: Configuration containing the API key and unit settings.

    Raises:
        ValueError: If the OPENWEATHER_API_KEY environment variable is missing.
    """
    # Obtain the API key from system environment variables
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY environment variable is required")
    return WeatherConfig(api_key=api_key)


async def _get(
    path: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Perform an asynchronous HTTP GET request to the OpenWeather API.

    Args:
        path: API endpoint path (e.g., 'weather' or 'forecast').
        params: Optional query parameters for the request.

    Returns:
        dict[str, Any]: The parsed JSON response from the API.
    """
    # Load current configuration settings
    config = get_config()
    params = params or {}

    # Inject API key and unit settings into the request parameters
    params["appid"] = config.api_key
    params["units"] = config.units

    # Use AsyncClient for efficient, non-blocking asynchronous HTTP requests
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{OPENWEATHER_BASE}/{path}", params=params)
        # Raise an exception for HTTP error statuses (4xx, 5xx)
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def get_weather(city: str) -> str:
    """Get current weather for a city.

    Args:
        city: City name (e.g. "Tokyo,JP" or "London,UK")
    """
    # Fetch current weather data for the specified city
    data = await _get("weather", {"q": city})
    # Format and return the raw JSON response as a clean string representation
    return _format_current(data)


@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city.

    Args:
        city: City name (e.g. "Tokyo,JP" or "London,UK")
        days: Number of days (1-5, default 3)
    """
    # Fetch weather forecast data for the specified city
    data = await _get("forecast", {"q": city})
    # Format and return the forecast details limited to the requested days
    return _format_forecast(data, days=days)


def _format_current(data: dict[str, Any]) -> str:
    """Format current weather data into a human-readable string.

    Args:
        data: The raw weather data dictionary from OpenWeather.

    Returns:
        str: Formatted description of the current weather.
    """
    # Unpack main metrics, weather state, and wind dictionary from raw data
    main_data = data["main"]
    weather = data["weather"][0]
    wind = data.get("wind", {})

    # Construct lines for clear text output visualization
    lines = [
        f"Weather in {data['name']}, {data.get('sys', {}).get('country', '')}:",
        f"  {weather['description'].title()}",
        f"  Temperature: {main_data['temp']}°C "
        f"(feels like {main_data['feels_like']}°C)",
        f"  Humidity: {main_data['humidity']}%",
        f"  Pressure: {main_data['pressure']} hPa",
        f"  Wind: {wind.get('speed', 'N/A')} m/s",
    ]
    return "\n".join(lines)


def _format_forecast(data: dict[str, Any], days: int = 3) -> str:
    """Format forecast weather data into a human-readable string.

    Args:
        data: The raw forecast data dictionary from OpenWeather.
        days: Number of days to include in the forecast output.

    Returns:
        str: Formatted description of the weather forecast.
    """
    # Unpack city metadata and the list of weather forecast intervals
    city = data["city"]
    intervals = data["list"]

    # OpenWeatherMap forecast provides data in 3-hour increments (8 intervals per day)
    intervals_per_day = 8
    total = min(days * intervals_per_day, len(intervals))

    lines = [
        f"Forecast for {city['name']}, {city.get('country', '')} "
        f"({days} day{'s' if days > 1 else ''}):"
    ]

    # Iterate over the intervals stepping by 1 full day (8 intervals) to get daily status
    for i in range(0, total, intervals_per_day):
        day_data = intervals[i]
        main_data = day_data["main"]
        weather = day_data["weather"][0]
        dt = day_data["dt_txt"]

        lines.append(f"\n  {dt}:")
        lines.append(f"    {weather['description'].title()}")
        lines.append(
            f"    {main_data['temp']}°C "
            f"(high {main_data['temp_max']}°C / low {main_data['temp_min']}°C)"
        )

    return "\n".join(lines)


def main() -> None:
    """Run the FastMCP server with HTTP transport."""
    # Launch FastMCP server; host on all interfaces (0.0.0.0) for remote access
    mcp.run(transport="http", host="0.0.0.0")


if __name__ == "__main__":
    main()


