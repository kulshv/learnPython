from google import genai
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import api_key

load_dotenv(Path(__file__).with_name(".env"))

def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Set it in Learn-Agent/.env "
            "or in your environment."
        )   

    client = genai.Client(api_key=api_key)

    interaction = client.interactions.create(
                     model="gemini-3-flash-preview",  
                     input="What is the weather like in Tokyo?"
                     )

    print(interaction.output_text)


if __name__ == "__main__":
    main()