# HRPolicyAI — Enterprise HR Policy RAG Assistant

[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![React Version](https://img.shields.io/badge/React-19.0-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Vector Database](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange.svg)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**HRPolicyAI** is an enterprise-grade Retrieval-Augmented Generation (RAG) assistant designed to accurately answer complex employee questions regarding company policies, leave entitlements, health benefits, code of conduct, and regional regulations (India, US, UK, Global).

HRPolicyAI features real-time token streaming, exact grounded citations with an interactive source inspection drawer, query caching for instant repeated answers, and real-time telemetry tracking for token costs and system performance.

---

## 📑 Table of Contents

1. [Key Features](#-key-features)
2. [Architecture Overview](#-architecture-overview)
3. [Project Structure](#-project-structure)
4. [Prerequisites](#-prerequisites)
5. [Environment Variables & Safe Secrets Configuration](#-environment-variables--safe-secrets-configuration)
6. [Step-by-Step Runnable Setup Guide](#-step-by-step-runnable-setup-guide)
   - [1. Backend Setup (FastAPI & Vector DB)](#1-backend-setup-fastapi--vector-db)
   - [2. Frontend Setup (React 19 + Vite)](#2-frontend-setup-react-19--vite)
7. [Demonstrating the Full End-to-End Flow](#-demonstrating-the-full-end-to-end-flow)
8. [Caching & Telemetry Engine](#-caching--telemetry-engine)
9. [API Endpoint Reference](#-api-endpoint-reference)
10. [Automated Verification & Benchmark Scripts](#-automated-verification--benchmark-scripts)
11. [Security & Compliance](#-security--compliance)

---

## 🚀 Key Features

- **⚡ Grounded RAG Pipeline**: High-accuracy semantic vector search powered by ChromaDB and state-of-the-art text embeddings.
- **🌊 Progressive SSE Streaming**: Fast streaming responses using Server-Sent Events (SSE) with smooth UI typing animation.
- **📚 Exact In-Text Citations**: Every claim is tagged with numbered source badges (e.g. `[1]`, `[2]`). Clicking a badge opens an inspection drawer showing chunk IDs, similarity scores, document titles, and source excerpts.
- **⚡ High-Performance Query Cache**: SHA-256 normalized hash caching (LRU + TTL) serves repeated queries in **< 2 ms** with **0 tokens consumed** and **100% cost savings**.
- **📊 Real-Time Telemetry & Token Cost Engine**: Automatically calculates prompt/completion token usage, computes costs against model rate cards, and writes structured audit logs to JSON Lines (`rag_requests.jsonl`).
- **🛡️ Multi-Region Policy Filtering**: Regional filters for India, United States, United Kingdom, and Global cross-region queries.
- **👥 Role-Based Access Control (RBAC)**: Switch between **Employee View** (conversational search, citation viewer) and **HR Admin View** (document ingestion, telemetry KPIs, request audit log, cache management).

---

## 🏗️ Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│               Frontend: React 19 + Vite                │
│  ┌──────────────────────┐    ┌──────────────────────┐  │
│  │  Employee Chat View  │    │ Admin Telemetry & KB │  │
│  │  - SSE Stream Reader │    │ - Cache KPI Cards    │  │
│  │  - Citation Drawer   │    │ - Audit Trail Table  │  │
│  └──────────────────────┘    └──────────────────────┘  │
└───────────────▲──────────────────────────▲─────────────┘
                │                          │
           HTTP / SSE                 HTTP REST
                │                          │
┌───────────────▼──────────────────────────▼─────────────┐
│             Backend API: FastAPI (Port 8000)            │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Query Cache Layer (SHA-256 Hash · LRU · TTL)     │  │
│  └────────────────────────▲─────────────────────────┘  │
│                           │ Cache Miss                  │
│  ┌────────────────────────▼─────────────────────────┐  │
│  │ ChromaDB Vector Retriever + Hybrid Re-ranker     │  │
│  └────────────────────────▲─────────────────────────┘  │
│                           │ Context & Policy Chunks     │
│  ┌────────────────────────▼─────────────────────────┐  │
│  │ LLM Generator (OpenAI / Azure / Compatible LLM)  │  │
│  └────────────────────────▲─────────────────────────┘  │
│                           │ Response Stream             │
│  ┌────────────────────────▼─────────────────────────┐  │
│  │ Telemetry Manager (JSONL Logger · Cost Engine)   │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```text
S82_HRPolicyAI_Sprint2/
│
├── frontend/                          # React 19 + Vite Frontend Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/                  # ChatContainer, ChatMessage, CitationInspector
│   │   │   ├── common/                # Navbar, Sidebar, RegionSelector
│   │   │   └── admin/                 # TelemetryCards, IngestionManager
│   │   ├── pages/                     # ChatInterface.jsx, AdminDashboard.jsx
│   │   ├── services/api.js            # Unified API Client with SSE Stream Support
│   │   └── App.jsx                    # Root Router & State Provider
│   ├── .env.example                   # Frontend environment template
│   ├── package.json                   # Vite & React dependencies
│   └── vite.config.js                 # Vite dev server configuration
│
├── rag-app-starter/                   # FastAPI Backend & RAG Engine
│   ├── data/                          # Raw HR policy source documents (.pdf, .txt)
│   ├── outputs/                       # Audit logs & telemetry outputs (Git tracked samples)
│   │   ├── rag_requests.jsonl         # Detailed JSON Lines request audit log
│   │   ├── rag_telemetry.log          # Plain text telemetry execution log
│   │   └── telemetry_summary.json     # Machine-readable usage & performance summary
│   ├── src/
│   │   ├── server.py                  # FastAPI server with SSE streaming & REST routes
│   │   ├── rag_pipeline.py            # Core RAG retrieval, vector search & synthesis
│   │   ├── telemetry_manager.py       # QueryCache, token counter, pricing & JSONL logger
│   │   ├── usage_report.py            # CLI benchmark and report generator
│   │   ├── e2e_demo.py                # Automated end-to-end verification script
│   │   └── vector_store.py            # ChromaDB vector store wrapper & chunk indexer
│   ├── .env.example                   # Backend environment template
│   └── requirements.txt               # Locked Python dependencies
│
├── USAGE_REPORT.md                    # Generated benchmark and cost analysis report
└── README.md                          # Complete developer and deployment documentation
```

---

## 📋 Prerequisites

Before running the application, ensure the following software is installed on your machine:

- **Python**: Version `3.9` through `3.12` ([Download Python](https://www.python.org/downloads/))
- **Node.js**: Version `18.0.0` or higher ([Download Node.js](https://nodejs.org/))
- **Git**: Installed and configured ([Download Git](https://git-scm.com/))
- **Operating System**: Compatible with Windows (PowerShell/CMD), macOS, or Linux.

---

## 🔐 Environment Variables & Safe Secrets Configuration

> [!IMPORTANT]
> **No API keys or sensitive credentials are ever hardcoded in the codebase.**
> All secrets and configurations are strictly loaded through environment variables via `.env` files, which are excluded from Git version control in `.gitignore`.

### 1. Backend Environment Configuration (`rag-app-starter/.env`)

Copy the template file to create your local `.env`:
```powershell
# Windows
copy rag-app-starter\.env.example rag-app-starter\.env

# macOS / Linux
cp rag-app-starter/.env.example rag-app-starter/.env
```

| Variable Name | Required | Default / Example | Description |
| :--- | :---: | :--- | :--- |
| `API_BASE_URL` | No | `https://api.openai.com/v1` | Base URL for OpenAI or custom proxy endpoint. |
| `OPENAI_API_KEY` | Yes* | `sk-proj-...` | Secret API key (*optional if using mock/local simulation mode). |
| `CHAT_MODEL` | No | `gpt-4o-mini` | LLM model name (`gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`). |
| `EMBEDDING_MODEL`| No | `text-embedding-3-small` | Model used for vector embeddings. |
| `CHROMA_DB_PATH` | No | `.chroma` | Directory for persistent ChromaDB storage. |
| `CHROMA_COLLECTION_NAME` | No | `hr_policy_chunks` | ChromaDB collection namespace. |
| `EMBEDDING_BATCH_SIZE` | No | `2` | Batch size for document embedding generation. |

### 2. Frontend Environment Configuration (`frontend/.env`)

Copy the template file to create your frontend `.env`:
```powershell
# Windows
copy frontend\.env.example frontend\.env

# macOS / Linux
cp frontend/.env.example frontend/.env
```

| Variable Name | Required | Default / Example | Description |
| :--- | :---: | :--- | :--- |
| `VITE_API_URL` | No | `http://localhost:8000` | URL of the running FastAPI backend server. |
| `VITE_USE_MOCK_API`| No | `false` | Set to `false` to connect to live backend API, or `true` for standalone offline demo. |

---

## 🏃 Step-by-Step Runnable Setup Guide

### 1. Backend Setup (FastAPI & Vector DB)

Open a terminal and navigate to the backend directory:

```powershell
# 1. Navigate to backend directory
cd rag-app-starter

# 2. Create Python virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Windows CMD:
.venv\Scripts\activate.bat
# On macOS / Linux:
source .venv/bin/activate

# 4. Install required dependencies
pip install -r requirements.txt

# 5. Start the FastAPI backend server
python src/server.py
```

The backend server will start at **`http://localhost:8000`**.
Interactive Swagger documentation is available at **`http://localhost:8000/docs`**.

---

### 2. Frontend Setup (React 19 + Vite)

Open a **second terminal** and run the following commands:

```powershell
# 1. Navigate to frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Start the Vite development server
npm run dev
```

The frontend application will start and be accessible in your browser at **`http://localhost:5173`**.

---

## 🔄 Demonstrating the Full End-to-End Flow

To experience or evaluate the complete user workflow:

1. **Open the Application**: Navigate to `http://localhost:5173` in your browser.
2. **Select Region**: Choose your region (e.g. `India`, `USA`, or `Global`) using the top navbar region selector.
3. **Ask a Policy Question**: Enter a question in the chat input, for example:
   > *"How many days of annual privilege leave am I entitled to in India?"*
4. **Observe Streaming Answer**: The answer streams progressively to the screen with citation markers like `[1]`, `[2]`.
5. **Inspect Citations**: Click on any citation badge `[1]` to open the **Source Citation Inspector** drawer. You can review the exact chunk ID, document title, section name, similarity score, and verbatim policy excerpt.
6. **Test Query Caching**: Re-send the same question or ask an identical query. Notice the **`⚡ Cached (Instant · 0.00s)`** badge and immediate sub-2ms response time.
7. **Inspect Admin Telemetry**: Switch to **HR Admin View** via the top navigation to inspect the live **Cache Hit Rate**, **Tokens Processed**, **Estimated Cost**, **Cost Saved**, and the searchable **Request Audit Trail**.

---

## ⚡ Caching & Telemetry Engine

HRPolicyAI features an integrated high-performance caching and telemetry layer:

- **Cache Implementation**: `QueryCache` class in [`src/telemetry_manager.py`](file:///rag-app-starter/src/telemetry_manager.py).
- **Key Derivation**: Normalized SHA-256 hash derived from lowercase trimmed query and region:
  ```python
  cache_key = hashlib.sha256(f"{query.strip().lower()}::{region.strip().lower()}".encode('utf-8')).hexdigest()
  ```
- **TTL & Eviction**: 1-hour configurable TTL with LRU cache eviction.
- **Audit Logging**: Every request is recorded with timestamps, query, preview, chunk IDs, cache hit/miss status, latency, tokens, and costs to [`outputs/rag_requests.jsonl`](file:///rag-app-starter/outputs/rag_requests.jsonl).

### Cost Calculation Reference

| Model | Prompt Tokens Rate (per 1M) | Completion Tokens Rate (per 1M) |
| :--- | :---: | :---: |
| `gpt-4o-mini` | $0.150 | $0.600 |
| `gpt-3.5-turbo` | $0.500 | $1.500 |
| `gpt-4o` | $2.500 | $10.000 |

---

## 📡 API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server health check and vector DB status. |
| `POST` | `/chat` | Standard RAG chat completion with grounded citations. |
| `POST` | `/chat/stream` | Server-Sent Events (SSE) progressive token streaming. |
| `GET` | `/telemetry/summary` | Aggregate analytics (hit rate %, latency, token counts, cost saved). |
| `GET` | `/telemetry/logs?limit=50` | Recent structured request audit trail from JSONL. |
| `POST` | `/telemetry/cache/clear` | Invalidate and purge all active query cache entries. |
| `GET` | `/documents` | List all indexed HR policy documents and chunks. |
| `POST` | `/documents/upload` | Upload new HR policy documents. |
| `POST` | `/documents/index` | Trigger vector embedding indexing on policy documents. |

---

## 🧪 Automated Verification & Benchmark Scripts

Run the included verification scripts directly from `rag-app-starter`:

### 1. Full End-to-End Pipeline Verification
```powershell
cd rag-app-starter
python src/e2e_demo.py
```
*Validates document indexing, RAG retrieval, citation verification, cache hit acceleration, and audit logging.*

### 2. Telemetry Benchmarking & Usage Report Generation
```powershell
cd rag-app-starter
python src/usage_report.py
```
*Executes automated benchmark queries, calculates latency distributions, exports [`outputs/telemetry_summary.json`](file:///rag-app-starter/outputs/telemetry_summary.json), and creates [`USAGE_REPORT.md`](file:///USAGE_REPORT.md).*

### 3. Frontend Production Build Verification
```powershell
cd frontend
npm run build
```
*Verifies type safety, module bundling, and zero compilation errors.*

---

## 🔒 Security & Compliance

1. **Secrets Isolation**: `.env` and all credential keys are strictly excluded from version control.
2. **Access Control**: Role-based access ensures employees cannot modify or delete backend policy knowledge chunks.
3. **Data Boundary**: Proprietary internal HR documents reside in local storage and ChromaDB vector embeddings without exposing raw databases to public repositories.
4. **Auditability**: Complete end-to-end request logging provides full compliance visibility into which employee queried which policy and what citations were provided.
