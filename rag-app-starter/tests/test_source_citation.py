"""
Unit tests for Assignment 3.40: Source Citation & Attribution.
Tests Tasks 1 through 5 using Python's standard unittest framework.
"""

import sys
import unittest
from pathlib import Path

# Add rag-app-starter to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.source_citation import (
    build_citation_map,
    assemble_context,
    build_cited_prompt,
    answer_with_citations,
    verify_citation,
    detect_fabricated_citations,
    sanitize_fabricated_citations,
    extract_citation_markers,
    POLICY_CORPUS,
)


class TestSourceCitation(unittest.TestCase):

    def setUp(self):
        self.sample_chunks = [
            {
                "id": "chunk_001",
                "text": "Employees receive 10 days of paid sick leave annually.",
                "metadata": {
                    "source": "sample_leave_policy.txt",
                    "chunk_id": "chunk_001",
                    "chunk_index": 0,
                    "section": "Sick Leave",
                    "page": 1,
                },
            },
            {
                "id": "chunk_002",
                "text": "Planned annual leave must be requested 14 calendar days in advance.",
                "metadata": {
                    "source": "sample_leave_policy.txt",
                    "chunk_id": "chunk_002",
                    "chunk_index": 1,
                    "section": "Leave Request",
                    "page": 2,
                },
            },
        ]

    def test_task1_and_task2_build_citation_map(self):
        """Task 1 & 2: Verify citation map structure and metadata mapping."""
        citation_map = build_citation_map(self.sample_chunks)
        self.assertIn("[1]", citation_map)
        self.assertIn("[2]", citation_map)

        # Check metadata fields
        chunk1 = citation_map["[1]"]
        self.assertEqual(chunk1["source"], "sample_leave_policy.txt")
        self.assertEqual(chunk1["chunk_id"], "chunk_001")
        self.assertEqual(chunk1["chunk_index"], 0)
        self.assertEqual(chunk1["section"], "Sick Leave")
        self.assertEqual(chunk1["page"], 1)
        self.assertIn("10 days of paid sick leave", chunk1["text"])

    def test_assemble_context_token_budget(self):
        """Verify context assembly respects token budget for efficiency."""
        context, token_count = assemble_context(self.sample_chunks, max_context_tokens=500)
        self.assertIn("[1]", context)
        self.assertIn("[2]", context)
        self.assertGreater(token_count, 0)
        self.assertLessEqual(token_count, 500)

    def test_build_cited_prompt(self):
        """Verify prompt contains strict grounding and citation instructions."""
        prompt = build_cited_prompt("How much sick leave is given?", self.sample_chunks)
        self.assertIn("Cite every factual claim using source markers like [1] or [2]", prompt)
        self.assertIn("do not invent citations", prompt)
        self.assertIn("How much sick leave is given?", prompt)

    def test_task3_citation_verification(self):
        """Task 3: Verify a citation marker against original source chunk text."""
        citation_map = build_citation_map(self.sample_chunks)
        answer = "Employees are entitled to 10 days of paid sick leave [1]."
        verification = verify_citation(answer, citation_map, "[1]")

        self.assertTrue(verification["verified"])
        self.assertEqual(verification["source"], "sample_leave_policy.txt")
        self.assertEqual(verification["chunk_id"], "chunk_001")
        self.assertEqual(verification["verification_status"], "CONFIRMED_GROUNDED")
        self.assertIn("10 days of paid sick leave", verification["original_text"])

    def test_task4_avoid_fabricated_citations_on_unsupported_query(self):
        """Task 4: Answers without sufficient supporting sources must return a fallback with 0 citations."""
        unsupported_query = "What is the policy for reimbursing personal gym memberships?"
        result = answer_with_citations(unsupported_query)

        self.assertFalse(result["grounded"])
        self.assertEqual(len(result["citations"]), 0)
        self.assertTrue(
            "not enough information" in result["answer"].lower()
            or "don't have enough information" in result["answer"].lower()
        )

    def test_task4_guardrail_detects_fabricated_citations(self):
        """Task 4 Guardrail: Detect and strip hallucinated markers."""
        citation_map = {"[1]": {"source": "doc.txt", "text": "real text"}}
        hallucinated_answer = "Policy says X [1] and Y [99]."

        fabricated = detect_fabricated_citations(hallucinated_answer, citation_map)
        self.assertEqual(fabricated, ["[99]"])

        sanitized = sanitize_fabricated_citations(hallucinated_answer, citation_map)
        self.assertEqual(sanitized, "Policy says X [1] and Y .")


if __name__ == "__main__":
    unittest.main()
