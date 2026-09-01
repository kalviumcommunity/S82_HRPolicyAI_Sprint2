ANSWER_TEMPLATE = """
You are a helpful RAG support assistant.

Answer the user's question using ONLY the provided context.
If the answer cannot be found in the context, say:
"I don't know based on the provided information."

Always be concise and accurate.

Context:
{context}

Question:
{question}
"""


def render_answer_prompt(context, question):
    return ANSWER_TEMPLATE.format(
        context=context,
        question=question
    )