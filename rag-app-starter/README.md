# HRPolicyAI — RAG Assistant Environment Starter

HRPolicyAI is an internal Retrieval-Augmented Generation (RAG) assistant that answers staff questions securely from a 4,000-document HR knowledge base. This directory is the **foundational workspace** — a clean, isolated, and reproducible environment that any teammate can clone and run without leaking secrets.

---

## Why This Matters

> An AI project with API keys is fundamentally different from a normal web app. A single leaked key means unauthorised billing, data exposure, and supply-chain risk. An isolated virtual environment combined with `.gitignore` + `.env.example` patterns guarantees that:
>
> - **Dependencies are pinned** — no "works on my machine" surprises.
> - **Secrets never touch git** — `.env` is ignored; only the template is committed.
> - **Local data stays local** — `data/` and `outputs/` are ignored by git.

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
