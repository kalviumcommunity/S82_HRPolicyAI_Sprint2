import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from prompts.answer import render_answer_prompt


def chat_feature(context, question):
    prompt = render_answer_prompt(
        context=context,
        question=question
    )

    print("=== CHAT FEATURE ===")
    print(prompt)

    return prompt


if __name__ == "__main__":
    context = """
    Employees can request a refund within 30 days of purchase.
    The product must be returned in its original condition.
    """

    question = "What is the refund window?"

    chat_feature(context, question)