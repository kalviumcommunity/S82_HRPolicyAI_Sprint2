import logging
import os

from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_client():
    base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")

    if not base_url:
        raise ValueError("OPENAI_BASE_URL is missing from .env")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from .env")

    return OpenAI(
        base_url=base_url,
        api_key=api_key
    )


def ask_hr_assistant():
    client = create_client()

    model = os.getenv("CHAT_MODEL")

    if not model:
        raise ValueError("CHAT_MODEL is missing from .env")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an HR assistant. "
                "Answer employee questions clearly and concisely."
            )
        },
        {
            "role": "user",
            "content": "What is the purpose of an employee leave policy?"
        }
    ]

    logging.info("REQUEST MESSAGES: %s", messages)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )

        answer = response.choices[0].message.content

        logging.info("RESPONSE: %s", answer)
        logging.info("USAGE: %s", response.usage)

        print("\nHR Assistant Response:")
        print(answer)

    except AuthenticationError:
        print("Authentication failed (401): check OPENAI_API_KEY in your .env file.")

    except RateLimitError:
        print("Rate limit exceeded (429): slow down or check your API quota.")

    except Exception as error:
        print(f"Unexpected API error: {error}")


if __name__ == "__main__":
    ask_hr_assistant()