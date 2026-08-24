# HRPolicyAI — RAG Assistant Environment Starter

HRPolicyAI is an internal Retrieval-Augmented Generation (RAG) assistant designed to securely and accurately answer employee questions using official HR documents (e.g., employee handbooks, leave policies, benefits policies, regional HR documents).

This repository contains the starter environment workspace, configuration files, and a basic runnable script to ensure a secure, isolated, and reproducible development setup before building out the pipeline.

## Problem Statement

HR departments handle voluminous, sensitive documents containing policies that vary by region or employment type. Manually addressing employee inquiries is time-consuming and error-prone. A RAG assistant provides instantaneous, context-grounded answers. However, during development, it is critical to keep proprietary internal HR documents, local databases, and private LLM API keys safe and secure, preventing accidental leaks to public version control systems.

This workspace establishes strict environment boundaries, security measures, and automated sanity testing to prepare for developers working on the codebase.

## Project Structure

```text
rag-app-starter/
│
├── data/
│   └── .gitkeep          # Local HR documents directory (Git ignored except .gitkeep)
│
├── src/
│   └── main.py           # Core source code / Health check entrypoint
│
├── prompts/
│   └── .gitkeep          # Directory for LLM prompts
│
├── outputs/
│   └── .gitkeep          # Local or generated outputs (Git ignored except .gitkeep)
│
├── .env.example          # Sample environment variables template
├── .gitignore            # Git exclusion rules
├── README.md             # Developer setup and instructions
└── requirements.txt      # Python dependencies with version constraints
```

## Prerequisites

- **Python**: Version 3.8 to 3.12 (recommended) installed on Windows. Ensure Python is added to your system `PATH`.
- **Git**: Installed and configured....

---

## Getting Started (Windows Setup)

Follow these steps to set up a clean, reproducible local development environment on Windows.

### 1. Clone and Navigate to the Project

Open PowerShell or Command Prompt, and navigate to the starter directory:
```powershell
cd rag-app-starter
```

### 2. Create the Virtual Environment

Create an isolated Python virtual environment named `.venv` to prevent dependency conflicts with global packages:
```powershell
python -m venv .venv
```

### 3. Activate the Virtual Environment

On Windows, activate the virtual environment depending on the shell you are using:

- **PowerShell**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
  *(Note: If you get a script execution policy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first)*

- **Command Prompt (CMD)**:
  ```cmd
  .venv\Scripts\activate.bat
  ```

Once activated, your terminal prompt will be prefixed with `(.venv)`.

### 4. Install Dependencies

Install the locked requirements from `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Create your local `.env` configuration file by copying `.env.example`:
```powershell
copy .env.example .env
```

#### Environment Variables Explanation

Open the newly created `.env` file and configure the variables:

| Variable Name | Description | Example / Allowed Values |
| :--- | :--- | :--- |
| `API_BASE_URL` | Base URL for the OpenAI-compatible proxy or alternative provider. | `https://api.openai.com/v1` |
| `OPENAI_API_KEY` | Your private secret API key used to authenticate request calls. | `sk-proj-...` |
| `CHAT_MODEL` | The LLM model to query for chat completions. | `gpt-4o` or `gpt-3.5-turbo` |
| `EMBEDDING_MODEL` | The text embedding model to use for vector searches. | `text-embedding-3-small` |

---

## Running the Application

Verify the environment is set up and working by executing the health check script:
```powershell
python src/main.py
```

### Expected Output
```text
Initializing HRPolicyAI Environment Health Check...
Python Version: 3.x.x
Successfully imported all required packages: python-dotenv, openai, chromadb.

Environment Configuration Status:
  API_BASE_URL:    Not Set
  OPENAI_API_KEY:  Not Configured
  CHAT_MODEL:      Not Set
  EMBEDDING_MODEL: Not Set

HRPolicyAI environment is ready.
```
---

## Security Guidelines

> [!CAUTION]
> **NEVER COMMIT PRIVATE CONFIGURATIONS AND HR DATA**
>
> 1. **Do not commit `.env`**: This file contains your private API keys. It is explicitly ignored in `.gitignore`.
> 2. **Do not place files in Git-monitored directories**: Keep raw HR policies in the `data/` folder and generated files in `outputs/`. The `.gitignore` file is configured to ignore all files in these directories (except `.gitkeep` placeholders).
> 3. **Verify Git Status**: Run `git status` before committing to verify that no secret files or environments are listed as untracked files.

---

## Clean Setup Verification

The setup verification is currently **In Progress / Pending Verification**.

Once local validation is executed, this status will be updated to **Verified** detailing the results of the fresh virtual environment installation.
