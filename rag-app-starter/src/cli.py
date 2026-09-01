from prompts.answer import render_answer_prompt


def batch_feature(context, question):
    prompt = render_answer_prompt(
        context=context,
        question=question
    )

    print("=== BATCH FEATURE ===")
    print(prompt)

    return prompt


if __name__ == "__main__":
    context = """
    Employees can request a refund within 30 days of purchase.
    The product must be returned in its original condition.
    """

    question = "Can I request a refund after 20 days?"

    batch_feature(context, question)