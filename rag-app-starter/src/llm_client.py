import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from prompts.prompt_templates import HR_SYSTEM_PROMPT

load_dotenv(dotenv_path=BASE_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_client():
    base_url = os.getenv("OPENAI_BASE_URL", os.getenv("API_BASE_URL"))
    api_key = os.getenv("OPENAI_API_KEY")

    if not base_url:
        raise ValueError("OPENAI_BASE_URL / API_BASE_URL is missing from .env")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from .env")

    return OpenAI(
        base_url=base_url,
        api_key=api_key
    )


def ask_hr_assistant(user_question=None, system_prompt=None):
    """
    Sends a query to the HR Assistant using separated system and user roles.
    
    :param user_question: The employee's question (User role).
    :param system_prompt: The behavioral instruction and constraints (System role).
    """
    client = create_client()
    model = os.getenv("CHAT_MODEL")

    if not model:
        raise ValueError("CHAT_MODEL is missing from .env")

    system_message = system_prompt or HR_SYSTEM_PROMPT
    question = user_question or "In 2 bullet points, summarize the standard paid annual leave entitlement for full-time employees."

    messages = [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": question
        }
    ]

    logging.info("REQUEST MESSAGES: %s", messages)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2
        )

        answer = response.choices[0].message.content

        logging.info("RESPONSE: %s", answer)
        logging.info("USAGE: %s", response.usage)

        print("\nHR Assistant Response:")
        print(answer)
        return answer

    except AuthenticationError:
        print("Authentication failed (401): check OPENAI_API_KEY in your .env file.")

    except RateLimitError:
        print("Rate limit exceeded (429): slow down or check your API quota.")

    except Exception as error:
        print(f"Unexpected API error: {error}")


if __name__ == "__main__":
    ask_hr_assistant()