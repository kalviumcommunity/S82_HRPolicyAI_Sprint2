# 3.13 Prompt Construction & System/User Roles

## Overview
This document details the prompt engineering design, system vs. user role separation, comparative evaluation of prompt variations, and rationale for the chosen prompt in the **HRPolicyAI** assistant.

---

## 1. System vs. User Roles (Task 1)

In conversational LLM architectures (like OpenAI Chat Completions), roles partition the instruction hierarchy:
- **`system` Role**: Sets the global identity, boundaries, behavioral rules, tone, scope constraints, format requirements, and refusal/fallback mechanisms. It acts as the assistant's permanent control panel across conversation turns.
- **`user` Role**: Contains the dynamic query or task input for the specific turn without needing to restate global behavioral rules.

---

## 2. System Message Architecture: Role, Scope & Constraints (Task 2)

The system prompt for **HRPolicyAI** is engineered with four explicit components:

```text
Role: You are an internal HR Policy Assistant for company employees.
Scope: Answer questions strictly based on official company HR policies (e.g., leave, benefits, working hours, code of conduct). Do NOT answer personal, financial, legal, or non-HR questions.
Constraints:
- Keep answers concise, factual, and strictly under 3 sentences unless bullet points are requested.
- Maintain a professional, supportive, and objective tone.
- Avoid speculation or fabricating policies.
Fallback: If the question is outside HR scope or the necessary policy information is missing/uncertain, respond with: 'I do not have sufficient policy information to answer this question. Please contact HR at hr-support@company.internal for assistance.'
```

### Breakdown:
1. **Role**: Identifies the assistant as an internal HR policy specialist.
2. **Scope**: Restricts answers to official HR policies; explicitly denies non-HR topics (legal/financial advice).
3. **Constraints**: Limits length (max 3 sentences / requested bullets), sets tone (professional, objective), and prevents fabrication/hallucination.
4. **Fallback**: Provides an exact standardized refusal response when info is missing or out of scope.

---

## 3. Comparison of Prompt Variations (Task 3)

We tested and evaluated multiple prompt variations:

| Variation | System Message | User Message | Output Characteristic |
| :--- | :--- | :--- | :--- |
| **Variation A: Vague & Unconstrained** | `You are a helpful assistant.` | `Tell me about leave.` | **Rambling & Generic**: Speculates across many leave types, guessing 10-25 days without specific grounding. |
| **Variation B: Clear & Constrained** *(Chosen)* | Full `HR_SYSTEM_PROMPT` (Role, Scope, Constraints, Fallback) | `In exactly 2 bullet points, summarize the standard paid annual leave policy for full-time employees. If information is not specified, state that you don't know.` | **Tight, Accurate & Structured**: Returns exactly 2 clear bullet points, strictly adhered to format and scope. |
| **Variation C: Out-of-Scope Guardrail Test** | Full `HR_SYSTEM_PROMPT` | `How should I invest my personal savings in cryptocurrency for maximum returns?` | **Deterministic Fallback**: Safely rejects non-HR financial query with the prescribed fallback message. |
| **Variation D: Output Format Constraint** | `JSON_SYSTEM_PROMPT` (Schema enforcement) | `What is the policy on annual leave entitlement?` | **Machine-Readable JSON**: Outputs pure JSON `{policy_topic, summary, action_required, confidence, fallback_triggered}` with zero extraneous text. |

---

## 4. Documentation of Chosen Prompt & Rationale (Task 4)

### Chosen System Prompt:
```text
Role: You are an internal HR Policy Assistant for company employees.
Scope: Answer questions strictly based on official company HR policies (e.g., leave, benefits, working hours, code of conduct). Do NOT answer personal, financial, legal, or non-HR questions.
Constraints:
- Keep answers concise, factual, and strictly under 3 sentences unless bullet points are requested.
- Maintain a professional, supportive, and objective tone.
- Avoid speculation or fabricating policies.
Fallback: If the question is outside HR scope or the necessary policy information is missing/uncertain, respond with: 'I do not have sufficient policy information to answer this question. Please contact HR at hr-support@company.internal for assistance.'
```

### Why This Prompt Works:
1. **Prevents Hallucinations**: Constraining the scope and mandating a deterministic fallback prevents the LLM from making up company rules or giving unverified advice.
2. **Predictable Formatting**: Length and structure constraints ensure outputs are easy for employees to digest quickly.
3. **Foundation for RAG Grounding**: Setting strict refusal rules prepares the system for retrieval-augmented generation (RAG), where the system prompt will enforce "answer only from retrieved context chunks".
4. **Safety & Compliance**: Explicitly blocks liability risks (e.g., providing legal or financial advice to employees).

---

## 5. Output Format Constraints (Follow-up Question)

To constrain the model to a specific output format (e.g., JSON):
- Explicitly describe the target schema in the `system` message.
- Use negative constraints (e.g. `Respond ONLY with valid JSON. Do not include markdown codeblocks or conversational filler.`).
- When using OpenAI API, enable `response_format={"type": "json_object"}` or use Structured Outputs / Pydantic schemas.

---

## 6. How to Run the Evaluation Script

```bash
# Execute prompt comparison suite
python rag-app-starter/src/prompt_comparison.py
```
Outputs will be logged to the console and saved to `rag-app-starter/outputs/prompt_comparison.md` and `rag-app-starter/outputs/comparison_results.json`.
