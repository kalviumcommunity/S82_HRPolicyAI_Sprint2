# HRPolicyAI — RAG Assistant Environment Starter

HRPolicyAI is an internal Retrieval-Augmented Generation (RAG) assistant that answers staff questions securely from a 4,000-document HR knowledge base. This directory is the **foundational workspace** — a clean, isolated, and reproducible environment that any teammate can clone and run without leaking secrets.

---

## Why This Matters

> An AI project with API keys is fundamentally different from a normal web app. A single leaked key means unauthorised billing, data exposure, and supply-chain risk. An isolated virtual environment combined with `.gitignore` + `.env.example` patterns guarantees that:
>
> - **Dependencies are pinned** — no "works on my machine" surprises.
> - **Secrets never touch git** — `.env` is ignored; only the template is committed.
> - **Local data stays local** — `data/` and `outputs/` are ignored by git.

The script also embeds a sample query with that same model, ranks the stored
chunks using cosine similarity, and writes the scores, source text, and
metadata to `outputs/similarity_results.json` and
`outputs/similarity_results.txt`. Cosine similarity compares vector direction,
which is useful for semantic relatedness because it reduces the effect of
embedding magnitude.

A companion demo, `python src/metadata_filtering_demo.py`, shows metadata
filtering and hybrid search. It compares unfiltered vs filtered top-k results,
then applies a lightweight keyword boost to create a hybrid ranking. The
resulting artifacts are written to `outputs/filtered_search_results.json` and
`outputs/filtered_search_results.txt`, including a sample precision comparison.

To run a retrieval tuning experiment, use `python src/retrieval_tuning_experiment.py`.
This script evaluates several retrieval settings (unfiltered vs section-filtered,
various `k` values, score thresholds, and hybrid ranking), measures top-1/top-k
hit rates plus average precision at k, and writes the comparison to
`outputs/retrieval_tuning_results.json` and
`outputs/retrieval_tuning_results.txt`.

For a re-ranking demo, run `python src/reranking_demo.py`. This script first
retrieves a larger candidate set, then applies a simple re-ranker that combines
vector similarity with lexical overlap. The generated artifacts in
`outputs/reranking_results.json` and `outputs/reranking_results.txt` show the
before-and-after ordering, the candidate set, and the final selected chunks.

To run a labelled retrieval evaluation, use `python src/retrieval_evaluation.py`.
This script stores a labelled query set in `outputs/labelled_queries.json`, then
measures recall@1/3/5 and precision@1/3/5 across the deterministic sample
corpus. The evaluation also records likely failure causes for any query that
misses the expected chunk or scores poorly, and writes the full results to
`outputs/retrieval_evaluation_results.json` and
`outputs/retrieval_evaluation_results.txt`.

### Batch processing and reruns

The embedding pipeline sends pending chunks in batches, retries rate-limit and
temporary provider errors with exponential backoff, and records failed batches
in `outputs/batch_run_summary.json`. Existing records are matched by their
text and metadata, so rerunning the script skips unchanged chunks. Configure
`EMBEDDING_BATCH_SIZE`, `EMBEDDING_MAX_RETRIES`, and
`EMBEDDING_COST_PER_1K_TOKENS` in `.env`; the readable totals are written to
`outputs/batch_run_summary.txt`.

---

## Project Structure

```text
rag-app-starter/
│
├── data/
│   └── .gitkeep          # HR document store — git-ignored, never committed
│
├── src/
│   └── main.py           # Environment health-check entrypoint
│
├── prompts/
│   ├── .gitkeep
│   └── prompt_templates.py  # Reusable system/user prompt definitions
│
├── outputs/
│   └── .gitkeep          # Generated files — git-ignored
│
├── .env.example          # ⬅ Template: copy to .env and fill in your keys
├── .gitignore            # Excludes .venv/, .env, data/, outputs/, node_modules/
├── README.md             # ← You are here
└── requirements.txt      # Pinned Python dependencies
```

### Directory purposes

| Directory | Purpose |
|-----------|---------|
| `data/` | Raw HR policy documents fed into the RAG pipeline. **Never committed.** |
| `src/` | Application source code — retrieval logic, LLM clients, utilities. |
| `prompts/` | LLM prompt templates and system instructions, versioned in git. |
| `outputs/` | Generated responses, evaluation logs, comparison reports. **Never committed.** |

---

## Prerequisites

- **Python 3.8 – 3.12** on your `PATH`
- **Git** installed and configured

---

## Setup Steps

### 1. Navigate into the starter directory

```powershell
cd rag-app-starter
```

### 2. Create an isolated virtual environment

```powershell
python -m venv .venv
```

This creates a `.venv/` folder that is **completely separate** from your global Python installation, preventing version conflicts with other projects.

### 3. Activate the virtual environment

**PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```
> If you see an execution-policy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first.

**Command Prompt (CMD):**
```cmd
.venv\Scripts\activate.bat
```

Your prompt will show `(.venv)` when active.

### 4. Install pinned dependencies

```powershell
pip install -r requirements.txt
```

This installs exactly:
- `openai>=1.0.0,<2.0.0` — LLM API client
- `chromadb>=0.4.0,<0.6.0` — local vector database
- `python-dotenv>=1.0.0,<2.0.0` — loads `.env` into `os.environ`

### 5. Copy the environment template

```powershell
copy .env.example .env
```

Open `.env` and fill in your real values:

| Variable | Description |
|----------|-------------|
| `API_BASE_URL` | OpenAI-compatible API base URL |
| `OPENAI_API_KEY` | Your **private** API key — never commit this |
| `CHAT_MODEL` | e.g. `gpt-4o-mini` |
| `EMBEDDING_MODEL` | e.g. `text-embedding-3-small` |

### 6. Run the health check

```powershell
python src/main.py
```

### 7. Generate sample embeddings

The embedding demo sends the prepared chunks as one batch to the configured
OpenAI-compatible API. Each returned vector is stored with its source text and
metadata in `outputs/embedding_results.json`; a readable verification report is
written to `outputs/embedding_results.txt`.

```powershell
python src/embeddings_demo.py
```

The report confirms the number of embedded chunks, common vector length, and
the first five values from each vector. Use the same `EMBEDDING_MODEL` when
embedding user queries so document and query vectors share one vector space.

### Embedding quality sanity checks

Run the repeatable offline smoke tests against the stored vectors:

```powershell
python src/embedding_quality_checks.py
```

This checks known query-to-chunk pairs, verifies the top source and chunk index,
and writes `outputs/embedding_quality_report.json` plus a readable
`outputs/embedding_quality_report.txt`. The report includes a deliberately
generic, borderline query to expose the limits of retrieval. To run the same
cases with the configured embedding API, use `python src/embedding_quality_checks.py --live`.

### Local vector database

The project uses a persistent local Chroma database. Configure its path and
collection name in `.env` with `CHROMA_DB_PATH` and `CHROMA_COLLECTION_NAME`,
then run:

```powershell
python src/vector_store.py
```

The script reads the stored embedding artifact, validates the common vector
dimension, creates or opens the collection with cosine distance, and inserts one
record containing the vector, source text, and chunk metadata. It reads the
record back and writes `outputs/vector_store_readback.json` and
`outputs/vector_store_readback.txt`. The local `.chroma/` database is ignored
by git; the readback report is committed as reproducible evidence.

---

## Expected Output (clean run — no `.env` values set)

```text
Initializing HRPolicyAI Environment Health Check...
Python Version: 3.x.x (...)
Successfully imported all required packages: python-dotenv, openai, chromadb.

Environment Configuration Status:
  API_BASE_URL:    Not Set
  OPENAI_API_KEY:  Not Configured
  CHAT_MODEL:      Not Set
  EMBEDDING_MODEL: Not Set

HRPolicyAI environment is ready.
```

---

## Clean-Run Verification — Confirmed

The setup was verified on **2026-08-31** on a fresh `.venv` (Windows 11, Python 3.11):

```
Initializing HRPolicyAI Environment Health Check...
Python Version: 3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)]
Successfully imported all required packages: python-dotenv, openai, chromadb.

Environment Configuration Status:
  API_BASE_URL:    Not Set
  OPENAI_API_KEY:  Not Configured
  CHAT_MODEL:      Not Set
  EMBEDDING_MODEL: Not Set

HRPolicyAI environment is ready.
```

**Status: VERIFIED** — all packages installed cleanly, health check passed, no secrets committed.

---

## How a Teammate Reproduces This From Scratch

```powershell
# 1. Clone the repo
git clone https://github.com/<your-org>/S82_HRPolicyAI_Sprint2.git
cd S82_HRPolicyAI_Sprint2/rag-app-starter

# 2. Create & activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure secrets (fill in real values)
copy .env.example .env

# 5. Run the health check
python src/main.py
```

That's it — five commands, fully reproducible.

---

## Security Guidelines

> [!CAUTION]
> **NEVER commit secrets or private data.**
>
> - `.env` — contains your API key. It is git-ignored. 
> - `data/` — contains HR documents. It is git-ignored.
> - `outputs/` — contains generated responses. It is git-ignored.
> - `.venv/` — your local Python environment. It is git-ignored.
>
> Run `git status` before every commit to confirm none of these appear as tracked files.
