# Assignment 3.40: Source Citation & Attribution Report

## Executive Summary
Grounded answers are stronger when users can verify them. This implementation connects answer claims back to retrieved source chunks using rich metadata (source file, section, chunk ID, chunk index, page).

## Task Breakdown & Verification

### Task 1: Source References in Generated Answers
Answers include discrete in-text citation markers (`[1]`, `[2]`) attached directly to each factual claim.
- **Sample Query**: How far in advance must a planned leave request be submitted?
- **Generated Answer**: `Planned leave must be requested via the internal HR Information Portal (HRIP) at least 14 calendar days in advance and requires manager approval [1].`

### Task 2: Mapping Citations to Chunk Metadata
Every citation marker corresponds to a structured metadata record:

| Marker | Document Source | Section | Chunk ID | Chunk Index | Page |
|---|---|---|---|---|---|
| `[1]` | sample_leave_policy.txt | 6. Request and Approval Process | `chunk_leave_004` | 3 | 2 |

### Task 3: Verifying Cited Sources Against Original Text
Users can inspect original text to confirm claims:
- **Inspected Marker**: `[1]`
- **Source File**: `sample_leave_policy.txt`
- **Section**: `6. Request and Approval Process`
- **Original Chunk Text**: *"All planned leave (annual PTO, parental leave) must be requested via the internal HR Information Portal (HRIP) at least 14 calendar days prior to the desired commencement date. Requests require formal electronic approval by the direct line manager."*
- **Verification Match**: **PASSED (100% Grounded)**

### Task 4: Avoiding Fabricated Citations & Fallback Handling
When retrieved context lacks supporting evidence, the system refuses to hallucinate facts or citations:
- **Unsupported Query**: *"What is the company reimbursement policy for employee gym memberships and personal fitness equipment?"*
- **Fallback Answer**: *"I do not have enough information in the provided context to answer this question."*
- **Citations Returned**: `{}` *(Empty dictionary, 0 fabricated citations)*
- **Guardrail Protection**: Hallucination scanner detected marker `[99]` and automatically removed it.

### Task 5: Sample Run Artifacts
- JSON data: `outputs/citation_results.json`
- Text summary: `outputs/citation_sample_answers.txt`
- Source code: `src/source_citation.py`
