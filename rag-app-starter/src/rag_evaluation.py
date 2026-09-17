import json
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from src.server import generate_rag_response
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY is not set. Evaluation may fail if using LLM as a judge.")

client = OpenAI(api_key=api_key) if api_key else None

test_set = [
    {
        "question": "How many weeks of maternity leave are provided in India?",
        "expected_points": ["26 weeks", "182 calendar days"],
        "expected_sources": {"India_Leave_Policy_2026.pdf"}
    },
    {
        "question": "What happens if I need medical leave for 4 days?",
        "expected_points": ["medical certificate is required", "consecutive absences exceeding 3 working days"],
        "expected_sources": {"India_Leave_Policy_2026.pdf"}
    },
    {
        "question": "What is the policy for space travel?",
        "expected_points": ["don't have enough reliable context"],
        "expected_sources": set()
    }
]

def judge_expected_points(answer, expected_points):
    """Score correctness 0 to 1 based on if expected points are covered."""
    answer_lower = answer.lower()
    covered = sum(1 for point in expected_points if point.lower() in answer_lower)
    return 1 if covered == len(expected_points) else 0

def judge_grounding(answer, retrieved_sources):
    """Score grounding 0 to 1 based on if the answer is supported by the retrieved sources."""
    sources_text = "\n".join([s.get("excerpt", "") for s in retrieved_sources]).lower()
    answer_lower = answer.lower()
    
    if not retrieved_sources:
        if "don't have enough reliable context" in answer_lower or "don't know" in answer_lower:
            return 1
        return 0

    # Simple heuristic: check if key words from answer exist in sources
    words = [w for w in answer_lower.split() if len(w) > 4]
    if not words:
        return 1
    
    matched = sum(1 for w in words if w in sources_text)
    return 1 if matched / len(words) > 0.5 else 0

def check_citations(citations, expected_sources):
    """Score citation accuracy 0 to 1."""
    if not expected_sources and not citations:
        return 1
    if not expected_sources and citations:
        return 0
        
    actual_sources = {c.get("document", "Unknown") for c in citations}
    # Match using document names
    if expected_sources.intersection(actual_sources):
        return 1
    # Fallback to loose matching
    if any(expected.replace('.pdf', '').replace('_', ' ') in actual for expected in expected_sources for actual in actual_sources):
        return 1
    return 0

def score_answer(example):
    answer, citations = generate_rag_response(example["question"])
    correctness = judge_expected_points(answer, example["expected_points"])
    grounding = judge_grounding(answer, citations)
    citation_accuracy = check_citations(citations, example["expected_sources"])
    return {
        "question": example["question"],
        "answer": answer,
        "correctness": correctness,
        "grounding": grounding,
        "citation_accuracy": citation_accuracy,
        "citations": citations
    }

def main():
    print("Running RAG Evaluation...")
    rows = [score_answer(example) for example in test_set]
    summary = {
        "questions": len(rows),
        "avg_correctness": sum(r["correctness"] for r in rows) / len(rows),
        "avg_grounding": sum(r["grounding"] for r in rows) / len(rows),
        "avg_citation_accuracy": sum(r["citation_accuracy"] for r in rows) / len(rows),
        "failures": [
            r for r in rows if min(r["correctness"], r["grounding"], r["citation_accuracy"]) < 1
        ]
    }
    
    print("\nEvaluation Summary:")
    print(json.dumps(summary, indent=2))
    
    # Save results
    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "rag_evaluation_results.json", "w") as f:
        json.dump({"details": rows, "summary": summary}, f, indent=2)
    print(f"Results saved to {output_dir / 'rag_evaluation_results.json'}")

if __name__ == "__main__":
    main()
