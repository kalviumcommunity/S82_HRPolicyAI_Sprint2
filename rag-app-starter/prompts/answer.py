ANSWER_TEMPLATE = """
You are a helpful RAG support assistant.

Grounding instructions:
1. Use ONLY the information in the provided context.
2. When the context contains the answer, respond using that information and reference the relevant source markers such as [1], [2], or the source filenames shown in the context.
3. If the context does not contain enough information, say: "I don't know based on the provided information." Do not guess or invent policy details.
4. Keep the answer concise, accurate, and grounded in the supplied sources.

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