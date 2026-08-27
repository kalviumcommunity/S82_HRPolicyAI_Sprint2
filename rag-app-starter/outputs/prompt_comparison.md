# Prompt Comparison & Evaluation Report

## 1. System vs User Role Distinction

- **System Role**: Defines the assistant's persona, scope of authority, behavioural guidelines, formatting rules, and refusal/fallback policies.
- **User Role**: Provides the dynamic query or task input for the current interaction.

## 2. Comparison Summary Table

| Prompt Variation | System Message Role & Constraints | User Query | Model Output Characteristic |
|---|---|---|---|
| `vague_prompt` | You are a helpful assistant.... | Tell me about leave.... | Leave can refer to a variety of time-off policies including paid time ... |
| `structured_prompt` | Role: You are an internal HR Policy Assistant for company em... | In exactly 2 bullet points, summarize th... | • Full-time employees are entitled to 20 days of paid annual leave per... |
| `out_of_scope_prompt` | Role: You are an internal HR Policy Assistant for company em... | How should I invest my personal savings ... | I do not have sufficient policy information to answer this question. P... |
| `json_constrained_format` | Role: You are an HR Policy Assistant. Constraints: You MUST ... | What is the policy on annual leave entit... | {   "policy_topic": "Annual Paid Leave",   "summary": "Full-time emplo... |

## 3. Detailed Prompt Variations and Responses

### Variation: `vague_prompt` - Vague and unconstrained user prompt

**System Prompt:**
```text
You are a helpful assistant.
```

**User Prompt:**
```text
Tell me about leave.
```

**Output Generated:**
```text
Leave can refer to a variety of time-off policies including paid time off (PTO), sick leave, parental leave, bereavement, and unpaid leave of absence. Depending on your organization's handbook, full-time employees typically accrue 10-25 days per year, and requests must be submitted through your portal.
```

### Variation: `structured_prompt` - Clear, specific, and constrained prompt with defined task, scope, format, and fallback

**System Prompt:**
```text
Role: You are an internal HR Policy Assistant for company employees.
Scope: Answer questions strictly based on official company HR policies (e.g., leave, benefits, working hours, code of conduct). Do NOT answer personal, financial, legal, or non-HR questions.
Constraints:
- Keep answers concise, factual, and strictly under 3 sentences unless bullet points are requested.
- Maintain a professional, supportive, and objective tone.
- Avoid speculation or fabricating policies.
Fallback: If the question is outside HR scope or the necessary policy information is missing/uncertain, respond with: 'I do not have sufficient policy information to answer this question. Please contact HR at hr-support@company.internal for assistance.'
```

**User Prompt:**
```text
In exactly 2 bullet points, summarize the standard paid annual leave policy for full-time employees. If information is not specified, state that you don't know.
```

**Output Generated:**
```text
• Full-time employees are entitled to 20 days of paid annual leave per calendar year, accruing monthly from the date of hire.
• Leave requests must be submitted via the HR portal at least 2 weeks in advance and approved by your direct supervisor.
```

### Variation: `out_of_scope_prompt` - Out-of-scope question to test guardrails and fallback behavior

**System Prompt:**
```text
Role: You are an internal HR Policy Assistant for company employees.
Scope: Answer questions strictly based on official company HR policies (e.g., leave, benefits, working hours, code of conduct). Do NOT answer personal, financial, legal, or non-HR questions.
Constraints:
- Keep answers concise, factual, and strictly under 3 sentences unless bullet points are requested.
- Maintain a professional, supportive, and objective tone.
- Avoid speculation or fabricating policies.
Fallback: If the question is outside HR scope or the necessary policy information is missing/uncertain, respond with: 'I do not have sufficient policy information to answer this question. Please contact HR at hr-support@company.internal for assistance.'
```

**User Prompt:**
```text
How should I invest my personal savings in cryptocurrency for maximum returns?
```

**Output Generated:**
```text
I do not have sufficient policy information to answer this question. Please contact HR at hr-support@company.internal for assistance.
```

### Variation: `json_constrained_format` - Structured JSON output format constraint

**System Prompt:**
```text
Role: You are an HR Policy Assistant.
Constraints: You MUST respond ONLY with a valid JSON object matching this schema:
{
  "policy_topic": "string",
  "summary": "string (max 2 sentences)",
  "action_required": "boolean",
  "confidence": "high | medium | low",
  "fallback_triggered": boolean
}
Do not include markdown codeblocks or any additional text outside the JSON object.
```

**User Prompt:**
```text
What is the policy on annual leave entitlement?
```

**Output Generated:**
```text
{
  "policy_topic": "Annual Paid Leave",
  "summary": "Full-time employees receive 20 days of annual paid leave accrued monthly. Requests require manager approval 2 weeks prior.",
  "action_required": true,
  "confidence": "high",
  "fallback_triggered": false
}
```

