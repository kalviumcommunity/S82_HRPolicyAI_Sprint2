import json
import logging
import os
from typing import Optional, Tuple, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("CHAT_MODEL")


# --------------------------------------------------
# Validate environment configuration
# --------------------------------------------------

if not BASE_URL:
    raise ValueError("OPENAI_BASE_URL is missing from .env")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY is missing from .env")

if not MODEL:
    raise ValueError("CHAT_MODEL is missing from .env")


# --------------------------------------------------
# Logging configuration
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# --------------------------------------------------
# Create OpenAI-compatible client
# --------------------------------------------------

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)


# --------------------------------------------------
# System prompt
# --------------------------------------------------

SYSTEM_PROMPT = """
You are an HR policy assistant.

Answer employee questions about HR policies.

You MUST return ONLY a valid JSON object.

Use exactly this structure:

{
    "answer": "string",
    "source": "string"
}

Rules:
1. "answer" must contain the answer to the employee's question.
2. "source" must contain the name of the HR policy document used.
3. Both fields are required.
4. Do not add markdown.
5. Do not add explanations outside the JSON object.
6. Do not use additional fields.
"""


# --------------------------------------------------
# Parse and validate JSON
# --------------------------------------------------

def parse_and_validate(
    raw_response: str
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:

    # Step 1: Parse JSON
    try:
        data = json.loads(raw_response)

    except json.JSONDecodeError:
        return None, "malformed JSON"

    # Step 2: Check that response is an object
    if not isinstance(data, dict):
        return None, "response is not a JSON object"

    # Step 3: Check required fields
    required_fields = ["answer", "source"]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return None, f"missing required fields: {missing_fields}"

    # Step 4: Validate field types
    if not isinstance(data["answer"], str):
        return None, "answer must be a string"

    if not isinstance(data["source"], str):
        return None, "source must be a string"

    # Step 5: Validate that fields are not empty
    if not data["answer"].strip():
        return None, "answer cannot be empty"

    if not data["source"].strip():
        return None, "source cannot be empty"

    return data, None


# --------------------------------------------------
# Call LLM
# --------------------------------------------------

def call_llm(question: str) -> Optional[Dict[str, Any]]:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": question
        }
    ]

    try:

        # ------------------------------------------
        # First API request
        # ------------------------------------------

        logging.info("Sending request to LLM")
        logging.info("REQUEST: %s", messages)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0
        )

        raw_response = response.choices[0].message.content

        logging.info("RAW RESPONSE: %s", raw_response)

        # ------------------------------------------
        # Parse first response
        # ------------------------------------------

        data, error = parse_and_validate(raw_response)

        if data is not None:

            logging.info("JSON parsed successfully")
            logging.info("VALIDATED DATA: %s", data)

            if response.usage:
                logging.info("TOKEN USAGE: %s", response.usage)

            return data

        # ------------------------------------------
        # First response failed validation
        # ------------------------------------------

        logging.warning(
            "First response failed validation: %s",
            error
        )

        # ------------------------------------------
        # Recovery request
        # ------------------------------------------

        recovery_messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": question
            },
            {
                "role": "user",
                "content": (
                    "Your previous response was invalid. "
                    "Return ONLY valid JSON with exactly "
                    "the fields 'answer' and 'source'. "
                    "Do not include any additional text."
                )
            }
        ]

        logging.info("Attempting recovery request")

        retry_response = client.chat.completions.create(
            model=MODEL,
            messages=recovery_messages,
            response_format={"type": "json_object"},
            temperature=0
        )

        retry_raw_response = (
            retry_response.choices[0].message.content
        )

        logging.info(
            "RECOVERY RESPONSE: %s",
            retry_raw_response
        )

        # ------------------------------------------
        # Parse recovery response
        # ------------------------------------------

        recovered_data, recovery_error = parse_and_validate(
            retry_raw_response
        )

        if recovered_data is not None:

            logging.info("Recovery successful")
            logging.info(
                "RECOVERED DATA: %s",
                recovered_data
            )

            return recovered_data

        logging.error(
            "Recovery failed: %s",
            recovery_error
        )

        return None

    except AuthenticationError:

        print(
            "Authentication failed (401): "
            "check OPENAI_API_KEY in your .env file."
        )

        return None

    except RateLimitError:

        print(
            "Rate limit exceeded (429): "
            "check your API quota or try again later."
        )

        return None

    except Exception as error:

        print(
            f"Unexpected API error: {error}"
        )

        return None


# --------------------------------------------------
# Test malformed JSON handling
# --------------------------------------------------

def test_malformed_json():

    print("\n")
    print("=" * 60)
    print("MALFORMED JSON TEST")
    print("=" * 60)

    # Intentionally invalid JSON
    malformed_response = """
    {
        "answer": "Employees can request leave through the HR portal.",
        "source": "Employee Leave Policy"
    """

    print("\nRaw malformed response:")
    print(malformed_response)

    data, error = parse_and_validate(
        malformed_response
    )

    if error:

        print("\nDetected error:")
        print(error)

    # Simulated recovered response
    recovered_response = """
    {
        "answer": "Employees can request leave through the HR portal.",
        "source": "Employee Leave Policy"
    }
    """

    print("\nRecovered response:")

    recovered_data, recovery_error = parse_and_validate(
        recovered_response
    )

    if recovered_data:

        print(
            json.dumps(
                recovered_data,
                indent=4
            )
        )

        print("\nRecovery successful.")

    else:

        print(
            f"Recovery failed: {recovery_error}"
        )


# --------------------------------------------------
# Test missing required field
# --------------------------------------------------

def test_missing_field():

    print("\n")
    print("=" * 60)
    print("MISSING FIELD TEST")
    print("=" * 60)

    invalid_response = """
    {
        "answer": "Employees can request leave through the HR portal."
    }
    """

    print("\nInvalid response:")
    print(invalid_response)

    data, error = parse_and_validate(
        invalid_response
    )

    if error:

        print("\nValidation result:")
        print(error)

    else:

        print(
            json.dumps(
                data,
                indent=4
            )
        )


# --------------------------------------------------
# Main program
# --------------------------------------------------

def main():

    print("=" * 60)
    print("HR POLICY ASSISTANT - STRUCTURED OUTPUT TEST")
    print("=" * 60)

    question = (
        "What is the purpose of an employee leave policy?"
    )

    print("\nEmployee question:")
    print(question)

    # ----------------------------------------------
    # Call the model
    # ----------------------------------------------

    result = call_llm(question)

    # ----------------------------------------------
    # Display result
    # ----------------------------------------------

    if result:

        print("\n")
        print("=" * 60)
        print("VALID STRUCTURED RESULT")
        print("=" * 60)

        print(
            json.dumps(
                result,
                indent=4
            )
        )

        print("\nAnswer:")
        print(result["answer"])

        print("\nSource:")
        print(result["source"])

    else:

        print(
            "\nThe model response could not be "
            "parsed or validated."
        )

    # ----------------------------------------------
    # Test malformed JSON
    # ----------------------------------------------

    test_malformed_json()

    # ----------------------------------------------
    # Test missing fields
    # ----------------------------------------------

    test_missing_field()


# --------------------------------------------------
# Run program
# --------------------------------------------------

if __name__ == "__main__":
    main()