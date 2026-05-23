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

#### 1. Running the MCP Server

The MCP server provides the weather tools.

**Standard Mode (HTTP):**
```bash
uv run weather-mcp
```
This starts the server on `http://0.0.0.0:8000` by default.

**Development/Testing Mode:**
To test the server with a built-in inspector, use:
```bash
uv run fastmcp dev weather_mcp/server.py
```
This opens a local web interface (usually at `http://localhost:6274`) to test the MCP tools directly.

#### 2. Running the Agent UI

The Weather Agent is a LangChain-powered chat interface that uses the tools provided by the server.

```bash
uv run weather-agent
```
Once started, you can access the Gradio UI at `http://localhost:7860`.

> **Note**: Ensure you have configured `OPENWEATHER_API_KEY` and `OPENROUTER_API_KEY` in your `.env` file before running the agent.

#### 3. Using with MCP Clients (e.g., Claude Desktop)

To use this server with the Claude Desktop app, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/kikki/Documents/code/weather-mcp",
        "run",
        "weather-mcp"
      ],
      "env": {
        "OPENWEATHER_API_KEY": "your_key_here"
      }
    }
  }
}
```
*(Adjust the directory path to your actual installation path)*

#### 4. Running with Docker

```bash
docker build -t weather-mcp .
docker run -p 7860:7860 --env-file .env weather-mcp
```

