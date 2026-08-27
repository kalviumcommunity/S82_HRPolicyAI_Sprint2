# Tokenization & Cost Estimation Analysis Report

## 1. What is a Token vs. Word vs. Character?

- **Character**: Individual letters, numbers, spaces, and punctuation marks (smallest textual unit).
- **Word**: Space-delimited semantic units.
- **Token**: The atomic numerical unit processed by LLMs via Byte-Pair Encoding (BPE). In English, 1 token is roughly 4 characters or ~0.75 words. Punctuation, symbols, and non-English scripts tokenize into more tokens.

## 2. Token Counts Across Varying Length Samples (Task 2)

| Sample Name | Category | Characters | Words | Tokens | Chars / Token | Words / Token |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Sample 1 (Short Question) | `query` | 92 | 18 | **19** | 4.84 | 0.95 |
| Sample 2 (Policy Paragraph) | `context_chunk` | 391 | 67 | **89** | 4.39 | 0.75 |
| Sample 3 (Full Policy Document) | `full_document` | 3080 | 487 | **668** | 4.61 | 0.73 |

## 3. Cost Estimation & Pricing Comparison (Task 3)

Cost calculated for a typical RAG query turn (**215 input tokens** [System + Query + Retrieved Context] and **60 output tokens** [Assistant Response]):

| Model | Input Rate (per 1M) | Output Rate (per 1M) | Cost per Single Query | Cost per 10,000 Queries |
| :--- | :--- | :--- | :--- | :--- |
| `gpt-4o-mini` | $0.15 | $0.60 | **$0.000068** | **$0.68** |
| `gpt-3.5-turbo` | $0.50 | $1.50 | **$0.000198** | **$1.98** |
| `gpt-4o` | $2.50 | $10.00 | **$0.001138** | **$11.38** |

### Corpus Scale Projection (4,000 Policy Documents):
- **Total Documents**: 4,000
- **Avg Tokens / Document**: 668
- **Total Corpus Token Count**: 2,672,000 tokens
- **One-Time Embedding Cost (`text-embedding-3-small`)**: **$0.0534**
- **Projected Monthly Query Cost (1,000 queries/day on `gpt-4o-mini`)**: **$2.05/month**

## 4. Length vs. Token Non-Linearity Analysis (Task 4)

Token counts track text length closely for standard English prose (~4.2 chars/token), but break down under specialized syntax, code, compound words, and non-Latin scripts:

| Text Category | Sample Excerpt | Chars | Words | Tokens | Chars / Token |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Standard English Prose** | `The company provides twenty days of paid annu...` | 87 | 14 | **15** | 5.8 |
| **Compound & Long Words** | `Antidisestablishmentarianism and internationa...` | 97 | 6 | **16** | 6.06 |
| **Python Code & Syntax** | `def calculate_pto(service_yrs: int) -> float:...` | 91 | 13 | **31** | 2.94 |
| **Multilingual (Hindi)** | `कंपनी सभी कर्मचारियों को प्रति वर्ष बीस दिन क...` | 74 | 14 | **70** | 1.06 |
| **Multilingual (Japanese)** | `会社はすべての従業員に年間20日の有給休暇を提供します。...` | 28 | 1 | **32** | 0.88 |
| **Formatted JSON Data** | `{"status": 200, "leave_days_remaining": 15, "...` | 75 | 6 | **23** | 3.26 |

## 5. Key Takeaways for RAG Architecture

1. **Context Window Protection**: Monitoring token counts prevents exceeding the context limits of the LLM.
2. **Input vs Output Cost Asymmetry**: Output tokens cost 3x to 4x more than input tokens. Enforcing strict concise answers saves direct operating expenditure.
3. **Optimal Chunking Strategy**: Knowing that standard HR text averages ~4.2 chars/token allows precise chunk size tuning (e.g., 500 token chunks ≈ 2,100 characters).
