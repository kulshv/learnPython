import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv(Path(__file__).with_name(".env"))


def get_current_weather(location: str) -> str:
    """Return sample weather data for the agent tool demonstration."""
    return f"The weather in {location} is sunny and 25°C."


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Set it in Learn-Agent/.env "
            "or in your environment."
        )

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        tools=[get_current_weather],
        system_instruction=(
            "You are a helpful assistant. Use the weather tool when asked "
            "about weather, and make clear that its data is sample data."
        ),
    )
    chat = client.chats.create(model="gemini-3-flash-preview", config=config)
    response = chat.send_message("What is the weather like in Tokyo?")
    print(response.text)


if __name__ == "__main__":
    main()
