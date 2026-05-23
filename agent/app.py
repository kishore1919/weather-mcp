"""LangChain-based Weather Agent and Gradio web interface."""

import os
from typing import Any, AsyncGenerator

from dotenv import load_dotenv
import gradio as gr
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openrouter import ChatOpenRouter

# Import the weather tools from our server implementation
from weather_mcp.server import get_forecast as _get_forecast
from weather_mcp.server import get_weather as _get_weather

# Load OpenRouter API credentials and models from environment variables
load_dotenv()


@tool
async def weather(city: str) -> str:
    """Get current weather for a city.

    Pass city name like 'Tokyo,JP' or 'London,UK'.
    """
    # Delegate to server's get_weather tool logic
    return await _get_weather(city)


@tool
async def forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city.

    Pass city name like 'Tokyo,JP' or 'London,UK'.
    """
    # Delegate to server's get_forecast tool logic
    return await _get_forecast(city, days)


# Define system-level instructions guiding the agent's behavior
SYSTEM_PROMPT = (
    "You are a helpful weather assistant. "
    "Use the weather and forecast tools to answer questions."
)


def create_agent_executor() -> Any:
    """Create and configure the LangChain agent executor.

    Returns:
        Any: The instantiated agent executor using OpenRouter LLM.

    Raises:
        ValueError: If OPENROUTER_API_KEY environment variable is not set.
    """
    # Check that required LLM API keys are present
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is required"
        )

    # Initialize the OpenRouter model client with low temperature for deterministic answers
    model = os.environ.get("MODEL")
    llm = ChatOpenRouter(
        model_name=model,
        temperature=0,
    )

    # Create the agent executor using standard LangChain tool orchestration
    return create_agent(
        model=llm,
        tools=[weather, forecast],
        system_prompt=SYSTEM_PROMPT,
    )


async def chat(message: str, history: list) -> AsyncGenerator[str, None]:
    """Process chat messages and yield agent responses.

    Args:
        message: The user's new input message.
        history: The list of prior messages in the conversation.

    Yields:
        str: The next chunk/response from the weather agent.
    """
    # Spin up the agent executor instance
    executor = create_agent_executor()

    messages = []
    # Loop through conversation history and format it into LangChain message objects
    for m in history:
        # Handle both newer object (Gradio 5) and dictionary format (legacy Gradio)
        if isinstance(m, dict):
            role = m.get("role")
            content = m.get("content")
        else:
            role = getattr(m, "role", None)
            content = getattr(m, "content", None)

        # Categorize message as HumanMessage or AIMessage based on role
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))

    # Append the user's latest incoming message
    messages.append(HumanMessage(content=message))

    # Invoke the agent asynchronously and yield the final message output
    result = await executor.ainvoke({"messages": messages})
    yield result["messages"][-1].content


def main() -> None:
    """Launch the Gradio interface for the weather agent."""
    # Define a clean chat web interface using Gradio ChatInterface
    gr.ChatInterface(
        fn=chat,
        title="Weather Agent",
        description="Ask about weather anywhere in the world.",
    ).launch(server_name="0.0.0.0")


if __name__ == "__main__":
    main()


