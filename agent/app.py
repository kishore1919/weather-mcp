import os
from typing import AsyncGenerator

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openrouter import ChatOpenRouter
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

from weather_mcp.server import get_weather as _get_weather
from weather_mcp.server import get_forecast as _get_forecast


@tool
async def weather(city: str) -> str:
    """Get current weather for a city. Pass city name like 'Tokyo,JP' or 'London,UK'."""
    return await _get_weather(city)


@tool
async def forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city. Pass city name like 'Tokyo,JP' or 'London,UK'."""
    return await _get_forecast(city, days)


SYSTEM_PROMPT = "You are a helpful weather assistant. Use the weather and forecast tools to answer questions."

def create_agent_executor():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is required")

    model = os.environ.get("MODEL")
    llm = ChatOpenRouter(
        model_name=model,
        temperature=0,
    )

    return create_agent(
        model=llm,
        tools=[weather, forecast],
        system_prompt=SYSTEM_PROMPT,
    )


async def chat(message: str, history: list) -> AsyncGenerator[str, None]:
    executor = create_agent_executor()
    
    messages = []
    for m in history:
        # Handle both object (Gradio 5) and dict (legacy)
        role = getattr(m, "role", m.get("role") if isinstance(m, dict) else None)
        content = getattr(m, "content", m.get("content") if isinstance(m, dict) else None)
        
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
            
    messages.append(HumanMessage(content=message))
    
    result = await executor.ainvoke({"messages": messages})
    yield result["messages"][-1].content


def main() -> None:
    gr.ChatInterface(
        fn=chat,
        title="Weather Agent",
        description="Ask about weather anywhere in the world.",
    ).launch(server_name="0.0.0.0")


if __name__ == "__main__":
    main()
