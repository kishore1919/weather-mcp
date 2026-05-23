import os
from typing import AsyncGenerator

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import gradio as gr

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


PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful weather assistant. Use the weather and forecast tools to answer questions."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
from langchain_openrouter import ChatOpenRouter

def create_agent() -> AgentExecutor:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is required")

    model = os.environ.get("MODEL", "google/gemini-2.0-flash-001")
    llm = ChatOpenRouter(
        model_name=model,
        temperature=0,
    )

    agent = create_openai_functions_agent(llm, [weather, forecast], PROMPT)
    return AgentExecutor(agent=agent, tools=[weather, forecast], verbose=False)


async def chat(message: str, history: list) -> AsyncGenerator[str, None]:
    executor = create_agent()
    result = await executor.ainvoke({"input": message, "chat_history": history or []})
    yield result["output"]


def main() -> None:
    gr.ChatInterface(
        fn=chat,
        title="Weather Agent",
        description="Ask about weather anywhere in the world.",
        type="messages",
    ).launch(server_name="0.0.0.0")


if __name__ == "__main__":
    main()
