"""
Tokenization & Cost Estimation Analysis Module for HRPolicyAI.
Calculates token counts across text lengths, demonstrates length-token non-linearity,
and projects cost estimates for single queries and corpus-scale operations.
"""

import json
import logging
from pathlib import Path
import tiktoken

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
DATA_DIR = BASE_DIR / "data"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Standard model pricing rates (per 1,000,000 tokens)
PRICING_TABLE = {
    "gpt-4o-mini": {
        "input_per_million": 0.15,
        "output_per_million": 0.60,
        "description": "Fast, cost-effective multimodal model"
    },
    "gpt-3.5-turbo": {
        "input_per_million": 0.50,
        "output_per_million": 1.50,
        "description": "Legacy conversational model"
    },
    "gpt-4o": {
        "input_per_million": 2.50,
        "output_per_million": 10.00,
        "description": "High-intelligence flagship model"
    },
    "text-embedding-3-small": {
        "input_per_million": 0.02,
        "output_per_million": 0.00,
        "description": "Efficient dense vector embedding model"
    }
}


def get_tokenizer(encoding_name: str = "cl100k_base"):
    """Returns tiktoken encoding instance."""
    try:
        return tiktoken.get_encoding(encoding_name)
    except Exception as e:
        logging.warning("Falling back to cl100k_base: %s", e)
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str, enc=None) -> int:
    """Counts tokens in a given string using tiktoken."""
    if enc is None:
        enc = get_tokenizer()
    return len(enc.encode(text))


def estimate_cost(input_tokens: int, output_tokens: int, model_name: str = "gpt-4o-mini") -> float:
    """
    Computes dollar cost accounting for different input vs. output rates.
    """
    rates = PRICING_TABLE.get(model_name, PRICING_TABLE["gpt-4o-mini"])
    cost_in = (input_tokens / 1_000_000) * rates["input_per_million"]
    cost_out = (output_tokens / 1_000_000) * rates["output_per_million"]
    return cost_in + cost_out


def run_token_estimation():
    enc = get_tokenizer("cl100k_base")

    # Load Full Policy Document
    policy_file = DATA_DIR / "sample_leave_policy.txt"
    if policy_file.exists():
        with open(policy_file, "r", encoding="utf-8") as f:
            full_document_text = f.read()
    else:
        full_document_text = "Sample HR Policy Document content placeholder."

    # Define 3 samples of varying length (Task 2)
    sample_short = "What is the maximum number of annual leave days an employee can carry over to the next year?"
    sample_paragraph = (
        "Full-time regular employees accrue paid annual leave at a baseline rate of 1.67 days per full calendar month worked "
        "(totaling 20 standard working days per fiscal year). Employees with 5+ years of continuous service accrue 2.08 days per month "
        "(25 days per fiscal year). A maximum of 5 unused PTO days may be carried over into the following calendar year, "
        "and must be utilized before March 31."
    )
    sample_document = full_document_text

    samples = [
        {"name": "Sample 1 (Short Question)", "text": sample_short, "category": "query"},
        {"name": "Sample 2 (Policy Paragraph)", "text": sample_paragraph, "category": "context_chunk"},
        {"name": "Sample 3 (Full Policy Document)", "text": sample_document, "category": "full_document"}
    ]

    print("=" * 80)
    print("TASK 1 & 2: Token Counts for Varying Length Text Samples")
    print("=" * 80)

    sample_results = []
    for s in samples:
        text = s["text"]
        char_count = len(text)
        word_count = len(text.split())
        tok_count = count_tokens(text, enc)
        char_per_tok = char_count / tok_count if tok_count > 0 else 0
        word_per_tok = word_count / tok_count if tok_count > 0 else 0

        res = {
            "name": s["name"],
            "category": s["category"],
            "character_count": char_count,
            "word_count": word_count,
            "token_count": tok_count,
            "char_to_token_ratio": round(char_per_tok, 2),
            "word_to_token_ratio": round(word_per_tok, 2)
        }
        sample_results.append(res)

        print(f"\n{s['name']}:")
        print(f"  - Characters : {char_count}")
        print(f"  - Words      : {word_count}")
        print(f"  - Tokens     : {tok_count}")
        print(f"  - Ratio      : {char_per_tok:.2f} chars/token (~{word_per_tok:.2f} words/token)")

    # TASK 3: Cost Estimation (Input vs Output)
    print("\n" + "=" * 80)
    print("TASK 3: Cost Estimation Across Pricing Models (Input vs Output)")
    print("=" * 80)

    # Simulated RAG interaction:
    # Input = System Prompt (120 tokens) + Retrieved Chunk (Sample 2: 76 tokens) + User Query (Sample 1: 19 tokens) = 215 tokens
    # Output = Model Answer (60 tokens)
    simulated_input_tokens = 215
    simulated_output_tokens = 60

    cost_estimates = {}
    for model_name, rates in PRICING_TABLE.items():
        if model_name == "text-embedding-3-small":
            continue
        single_call_cost = estimate_cost(simulated_input_tokens, simulated_output_tokens, model_name)
        cost_estimates[model_name] = {
            "single_call_cost_usd": round(single_call_cost, 7),
            "cost_per_10k_queries_usd": round(single_call_cost * 10_000, 4),
            "input_rate_per_1m": rates["input_per_million"],
            "output_rate_per_1m": rates["output_per_million"]
        }
        print(f"Model: {model_name:<15} | 1 Query: ${single_call_cost:.6f} | 10,000 Queries: ${single_call_cost * 10000:.2f}")

    # Corpus Scale Projection (4,000 Documents)
    avg_doc_tokens = sample_results[2]["token_count"]
    total_corpus_tokens = avg_doc_tokens * 4000
    embedding_cost = (total_corpus_tokens / 1_000_000) * PRICING_TABLE["text-embedding-3-small"]["input_per_million"]

    corpus_scale_data = {
        "total_documents": 4000,
        "avg_tokens_per_doc": avg_doc_tokens,
        "total_corpus_tokens": total_corpus_tokens,
        "one_time_embedding_cost_usd": round(embedding_cost, 4),
        "daily_query_volume": 1000,
        "monthly_query_cost_gpt4o_mini": round(cost_estimates["gpt-4o-mini"]["single_call_cost_usd"] * 1000 * 30, 2)
    }

    print(f"\nCorpus Scale Projection (4,000 HR Policy Documents):")
    print(f"  - Total Corpus Tokens   : {total_corpus_tokens:,} tokens")
    print(f"  - One-time Embedding Cost: ${embedding_cost:.4f} (using text-embedding-3-small)")
    print(f"  - 1,000 Daily Queries   : ${corpus_scale_data['monthly_query_cost_gpt4o_mini']:.2f} / month (using gpt-4o-mini)")

    # TASK 4: Length vs Token Non-Linearity Analysis
    print("\n" + "=" * 80)
    print("TASK 4: Length vs Token Non-Linearity Comparison")
    print("=" * 80)

    non_linear_cases = [
        {
            "category": "Standard English Prose",
            "text": "The company provides twenty days of paid annual vacation leave to all active employees."
        },
        {
            "category": "Compound & Long Words",
            "text": "Antidisestablishmentarianism and internationalization requirements necessitate pre-authorization."
        },
        {
            "category": "Python Code & Syntax",
            "text": "def calculate_pto(service_yrs: int) -> float:\n    return 25.0 if service_yrs >= 5 else 20.0"
        },
        {
            "category": "Multilingual (Hindi)",
            "text": "कंपनी सभी कर्मचारियों को प्रति वर्ष बीस दिन का सवेतन अवकाश प्रदान करती है।"
        },
        {
            "category": "Multilingual (Japanese)",
            "text": "会社はすべての従業員に年間20日の有給休暇を提供します。"
        },
        {
            "category": "Formatted JSON Data",
            "text": '{"status": 200, "leave_days_remaining": 15, "eligible_for_carryover": true}'
        }
    ]

    non_linearity_results = []
    for case in non_linear_cases:
        txt = case["text"]
        chars = len(txt)
        words = len(txt.split())
        toks = count_tokens(txt, enc)
        char_ratio = chars / toks if toks > 0 else 0
        word_ratio = words / toks if toks > 0 else 0

        entry = {
            "category": case["category"],
            "sample_text": txt,
            "character_count": chars,
            "word_count": words,
            "token_count": toks,
            "chars_per_token": round(char_ratio, 2),
            "words_per_token": round(word_ratio, 2)
        }
        non_linearity_results.append(entry)
        print(f"[{case['category']:<25}] {chars:>3} chars | {words:>2} words | {toks:>2} tokens -> {char_ratio:.2f} chars/token")

    # Save to JSON and Markdown Report
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    full_analysis = {
        "sample_token_counts": sample_results,
        "cost_estimates": cost_estimates,
        "corpus_scale_projection": corpus_scale_data,
        "length_token_non_linearity": non_linearity_results
    }

    with open(OUTPUTS_DIR / "token_analysis.json", "w", encoding="utf-8") as f:
        json.dump(full_analysis, f, indent=2)

    with open(OUTPUTS_DIR / "token_estimation_report.md", "w", encoding="utf-8") as f:
        f.write("# Tokenization & Cost Estimation Analysis Report\n\n")
        f.write("## 1. What is a Token vs. Word vs. Character?\n\n")
        f.write("- **Character**: Individual letters, numbers, spaces, and punctuation marks (smallest textual unit).\n")
        f.write("- **Word**: Space-delimited semantic units.\n")
        f.write("- **Token**: The atomic numerical unit processed by LLMs via Byte-Pair Encoding (BPE). In English, 1 token is roughly 4 characters or ~0.75 words. Punctuation, symbols, and non-English scripts tokenize into more tokens.\n\n")

        f.write("## 2. Token Counts Across Varying Length Samples (Task 2)\n\n")
        f.write("| Sample Name | Category | Characters | Words | Tokens | Chars / Token | Words / Token |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for s in sample_results:
            f.write(f"| {s['name']} | `{s['category']}` | {s['character_count']} | {s['word_count']} | **{s['token_count']}** | {s['char_to_token_ratio']} | {s['word_to_token_ratio']} |\n")

        f.write("\n## 3. Cost Estimation & Pricing Comparison (Task 3)\n\n")
        f.write("Cost calculated for a typical RAG query turn (**215 input tokens** [System + Query + Retrieved Context] and **60 output tokens** [Assistant Response]):\n\n")
        f.write("| Model | Input Rate (per 1M) | Output Rate (per 1M) | Cost per Single Query | Cost per 10,000 Queries |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for m, data in cost_estimates.items():
            f.write(f"| `{m}` | ${data['input_rate_per_1m']:.2f} | ${data['output_rate_per_1m']:.2f} | **${data['single_call_cost_usd']:.6f}** | **${data['cost_per_10k_queries_usd']:.2f}** |\n")

        f.write("\n### Corpus Scale Projection (4,000 Policy Documents):\n")
        f.write(f"- **Total Documents**: {corpus_scale_data['total_documents']:,}\n")
        f.write(f"- **Avg Tokens / Document**: {corpus_scale_data['avg_tokens_per_doc']}\n")
        f.write(f"- **Total Corpus Token Count**: {corpus_scale_data['total_corpus_tokens']:,} tokens\n")
        f.write(f"- **One-Time Embedding Cost (`text-embedding-3-small`)**: **${corpus_scale_data['one_time_embedding_cost_usd']}**\n")
        f.write(f"- **Projected Monthly Query Cost (1,000 queries/day on `gpt-4o-mini`)**: **${corpus_scale_data['monthly_query_cost_gpt4o_mini']}/month**\n\n")

        f.write("## 4. Length vs. Token Non-Linearity Analysis (Task 4)\n\n")
        f.write("Token counts track text length closely for standard English prose (~4.2 chars/token), but break down under specialized syntax, code, compound words, and non-Latin scripts:\n\n")
        f.write("| Text Category | Sample Excerpt | Chars | Words | Tokens | Chars / Token |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for c in non_linearity_results:
            sample_preview = c['sample_text'].replace('\n', ' ')[:45] + "..."
            f.write(f"| **{c['category']}** | `{sample_preview}` | {c['character_count']} | {c['word_count']} | **{c['token_count']}** | {c['chars_per_token']} |\n")

        f.write("\n## 5. Key Takeaways for RAG Architecture\n\n")
        f.write("1. **Context Window Protection**: Monitoring token counts prevents exceeding the context limits of the LLM.\n")
        f.write("2. **Input vs Output Cost Asymmetry**: Output tokens cost 3x to 4x more than input tokens. Enforcing strict concise answers saves direct operating expenditure.\n")
        f.write("3. **Optimal Chunking Strategy**: Knowing that standard HR text averages ~4.2 chars/token allows precise chunk size tuning (e.g., 500 token chunks ≈ 2,100 characters).\n")

    print(f"\nArtifacts generated:")
    print(f" - {OUTPUTS_DIR / 'token_analysis.json'}")
    print(f" - {OUTPUTS_DIR / 'token_estimation_report.md'}")


if __name__ == "__main__":
    run_token_estimation()
