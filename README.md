# Weather MCP & Agent

An MCP (Model Context Protocol) server for the OpenWeather API, featuring an integrated AI agent built with LangChain and Gradio.

## Features

- **Weather MCP Server**: A FastMCP-based server that provides tools to get current weather, forecasts, and air quality data.
- **Weather Agent**: A conversational agent that uses the MCP server to answer weather-related questions.
- **Gradio UI**: A web interface to interact with the Weather Agent.
- **Docker Ready**: Easily deployable using Docker.

## Project Structure

- `weather_mcp/`: The MCP server implementation.
- `agent/`: The LangChain agent and Gradio UI.
- `Dockerfile`: Multi-stage build for the entire project.
- `pyproject.toml`: Project metadata and dependencies (using `uv`).

## Getting Started

### Prerequisites

- [uv](https://github.com/astral-sh/uv) (recommended) or Python 3.10+
- OpenWeather API Key (from [openweathermap.org](https://openweathermap.org/))
- OpenRouter API Key (from [openrouter.ai](https://openrouter.ai/))

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd weather-mcp
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

### Usage

#### Running the MCP Server
```bash
uv run weather-mcp
```

#### Running the Agent UI
```bash
uv run weather-agent
```

#### Running with Docker
```bash
docker build -t weather-mcp .
docker run -p 7860:7860 --env-file .env weather-mcp
```

## License

MIT
