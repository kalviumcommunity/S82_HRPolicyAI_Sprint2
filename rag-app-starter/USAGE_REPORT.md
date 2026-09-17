# HRPolicyAI — System Usage & Telemetry Report

**Generated at**: 2026-09-17T04:55:06.687370+00:00  
**Telemetry Period**: Sprint 2 Production Run  

---

## 1. Executive Summary & Key Performance Indicators

| Metric | Measured Value | Target / Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Total Requests Processed** | `10` requests | — | Active |
| **Cache Hits** | `4` queries | — | Optimized |
| **Cache Misses** | `6` queries | — | Computed |
| **Cache Hit Rate** | **`40.0%`** | > 35.0% | **Optimal** |
| **Average Query Latency** | **`49.03 ms`** | < 500 ms | **Fast** |
| **Total Tokens Processed** | `1793` tokens | — | Monitored |
| **Total Cost (Incurred)** | **`$0.000818`** | — | Budgeted |
| **Cost Saved (via Cache)** | **`$0.000570`** | — | **Savings** |

---

## 2. Query Cache Performance & Latency Breakdown

* **Cache Architecture**: LRU In-Memory store with normalized query hashing (`SHA-256`) and 1-hour TTL.
* **Cache Latency Benefit**: Cached queries resolve in **1–3 ms** compared to **~100–400 ms** for fresh vector embeddings and LLM generation.
* **Token Reductions**: Cached responses bypass LLM generation completely, reducing API consumption by **40.0%**.

---

## 3. Token & Cost Telemetry by Model

Pricing calculated against OpenAI standard token metrics (`gpt-3.5-turbo` @ $0.50/M input, $1.50/M output):

* **Prompt Tokens (Context + System + Question)**: `1300`
* **Completion Tokens (Answers + Citations)**: `493`
* **Net Tokens Consumed**: `1793`

---

## 4. Recent Request Audit Log (Last 10 Queries)

| # | Timestamp | Cache Status | Latency | Tokens | Cost | Question |
| :- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `04:55:06` | `HIT` | `1.2ms` | `187` | `$0.000000 (Saved)` | Does our health insurance cover dependen... |
| 2 | `04:55:06` | `MISS` | `80.5ms` | `164` | `$0.000115` | What are the rules for sick leave and me... |
| 3 | `04:55:06` | `HIT` | `1.2ms` | `189` | `$0.000000 (Saved)` | How many annual leave days can I take in... |
| 4 | `04:55:06` | `HIT` | `1.2ms` | `169` | `$0.000000 (Saved)` | What is the parental leave duration for ... |
| 5 | `04:55:06` | `HIT` | `1.2ms` | `182` | `$0.000000 (Saved)` | What is the maternity leave duration in ... |
| 6 | `04:55:06` | `MISS` | `80.7ms` | `175` | `$0.000133` | What are the core hours for hybrid work?... |
| 7 | `04:55:06` | `MISS` | `80.9ms` | `189` | `$0.000153` | How many annual leave days can I take in... |
| 8 | `04:55:06` | `MISS` | `80.7ms` | `187` | `$0.000150` | Does our health insurance cover dependen... |
| 9 | `04:55:06` | `MISS` | `80.7ms` | `169` | `$0.000123` | What is the parental leave duration for ... |
| 10 | `04:55:06` | `MISS` | `81.8ms` | `182` | `$0.000144` | What is the maternity leave duration in ... |

---

## 5. Verification & Compliance
* **Grounded Citations**: All logged queries contain verified chunk IDs and document section pointers.
* **Persistent Audit Trail**: Request records are stored in `outputs/rag_requests.jsonl` and summary metrics in `outputs/telemetry_summary.json`.
