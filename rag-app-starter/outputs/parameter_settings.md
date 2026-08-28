# Recommended Model Settings for Grounded RAG Tasks

When building a Retrieval-Augmented Generation (RAG) assistant, the goal is for the model to synthesize and report the retrieved context faithfully without inventing details (hallucination) or drifting off-topic.

The following parameter settings are recommended for a grounded, factual task:

## 1. Temperature: Low (0.0 to 0.2)
- **Why**: Temperature controls the randomness of the output. A low temperature makes the model more focused, consistent, and repeatable. 
- **Effect**: It forces the model to choose the most probable tokens based heavily on the retrieved context rather than getting "creative" and fabricating information.

## 2. Max Tokens: Sensible Cap (e.g., 200 - 400)
- **Why**: Output tokens are directly tied to API costs. A RAG assistant should ideally provide concise answers based on context.
- **Effect**: Caps the length of the response, protecting against runaway answers, rambling, and unexpected high costs.

## 3. Stop Sequence: Optional but useful (e.g., `["\n\nUser:", "Observation:"]`)
- **Why**: Stop sequences instruct the model to halt generation when a specific text string is produced.
- **Effect**: Prevents the model from hallucinating subsequent turns of conversation or rambling past the direct answer to the question.

### Summary
For a factual HR assistant, always use **low temperature (e.g. 0.1)** to ensure strict adherence to HR policies, a **defined max_tokens** to keep answers brief and on-budget, and **stop sequences** to prevent over-generation.
