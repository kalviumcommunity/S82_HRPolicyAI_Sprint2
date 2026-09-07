# HRPolicyAI — Frontend Application

Production-ready React + Vite frontend for **HRPolicyAI**, an internal Retrieval-Augmented Generation (RAG) assistant designed for enterprise HR policy search, grounded citations, and knowledge base administration.

---

## Key Features

- **Employee Workspace**:
  - **Conversational RAG Assistant (`/chat`)**: Multi-turn chat interface grounded in official indexed HR documents with auto-scroll, keyboard shortcuts (Enter to send, Shift+Enter for newline), prompt chips, and loading states.
  - **Verifiable Citations & Source Excerpts**: Every AI response displays compact source cards with document name, section, page, and version. Clicking "View Source Excerpt" opens a detailed modal with the verbatim text chunk retrieved from vector search.
  - **Conversation History (`/history`)**: Search, filter, resume, or delete prior policy consultations.
  - **Employee Profile & Jurisdiction Preferences (`/profile`)**: Regional policy settings (India, USA, UK, Singapore, Europe, APAC, Global).

- **HR Admin Workspace**:
  - **Knowledge Base Dashboard (`/admin`)**: Real-time metrics on total documents, indexed status, ChromaDB vector chunks, and indexing errors.
  - **Document Repository Management (`/admin/documents`)**: Filter documents by region, category, or status. Re-index corrupted files and delete obsolete policies.
  - **Multi-Format Upload Modal**: Drag & drop ingestion for PDF and Word (`.docx`) files with metadata extraction and simulated vector embedding.

- **Role-Based Routing & Security**:
  - `EMPLOYEE`: Access to Chat, History, and Profile.
  - `HR_ADMIN`: Full access to employee workspace + Admin Dashboard and Document Management.
  - `ProtectedRoute`: Client-side route guarding with redirection.
  - Role switcher quick-toggle for demonstration and QA.

- **Architecture & Backend Compatibility**:
  - Zero coupling to mock implementation.
  - Centralized API service layer (`src/services/api.js`) and centralized mock data (`src/data/mockData.js`).
  - Switch to live FastAPI + ChromaDB backend by setting `VITE_USE_MOCK_API=false`.

---

## Directory Structure

```text
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.jsx           # Responsive sidebar with role sections
│   │   │   ├── Topbar.jsx            # Header with status pills and mobile trigger
│   │   │   └── PageContainer.jsx     # Responsive application shell
│   │   ├── chat/
│   │   │   ├── ChatMessage.jsx       # User query & AI citation layout
│   │   │   ├── ChatInput.jsx         # Auto-expanding composer with suggestions
│   │   │   ├── SourceCard.jsx        # Compact citation card
│   │   │   └── SourceModal.jsx       # Modal showing full policy excerpt
│   │   ├── history/
│   │   │   └── ConversationCard.jsx  # Past query card with preview
│   │   ├── documents/
│   │   │   ├── DocumentTable.jsx     # Document table with metadata modal
│   │   │   ├── DocumentStatus.jsx    # Status pills (Indexed, Processing, Failed)
│   │   │   └── UploadDocumentModal.jsx # Drag & drop upload with metadata fields
│   │   └── common/
│   │       ├── Button.jsx            # Accessible button with variants & loading
│   │       ├── Modal.jsx             # Accessible modal dialog
│   │       ├── Loading.jsx           # Loading spinner & status indicator
│   │       ├── EmptyState.jsx        # Empty state with call-to-action
│   │       └── ErrorState.jsx        # Error alert with retry action
│   ├── pages/
│   │   ├── Login.jsx                 # Login with demo accounts & validation
│   │   ├── Register.jsx              # Employee registration
│   │   ├── Chat.jsx                  # Primary employee RAG chat screen
│   │   ├── History.jsx               # Searchable conversation history
│   │   ├── Profile.jsx               # Employee identity & jurisdiction
│   │   ├── AdminDashboard.jsx        # Metrics & knowledge base table
│   │   └── Documents.jsx             # Document search, filters, & management
│   ├── services/
│   │   └── api.js                    # Centralized API service (Mock & FastAPI)
│   ├── context/
│   │   └── AuthContext.jsx           # Authentication & role state
│   ├── data/
│   │   └── mockData.js               # Centralized mock users, docs, QA pairs
│   ├── routes/
│   │   └── ProtectedRoute.jsx        # Route guard enforcing authentication & roles
│   ├── App.jsx                       # Main application router
│   ├── index.css                     # Tailwind CSS v4 design tokens
│   └── main.jsx                      # React entrypoint
├── package.json
└── vite.config.js
```

---

## Getting Started

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Run Development Server
```bash
npm run dev
```
The app runs at `http://localhost:5173`.

Alternatively, from the repository root:
```bash
npm run dev
```

### 3. Build for Production
```bash
npm run build
```

---

## Connecting to the FastAPI Backend

To switch from mock data to the live FastAPI + ChromaDB backend:

1. Create a `.env` file in `frontend/`:
   ```env
   VITE_USE_MOCK_API=false
   VITE_API_URL=http://localhost:8000
   ```
2. Expected backend endpoints:
   - `POST /auth/login` → `{ token, user }`
   - `POST /auth/register` → `{ token, user }`
   - `GET /auth/me` → `{ user }`
   - `POST /chat` → `{ conversation_id, message_id, answer, sources: [{ document, section, page, region, version, excerpt }] }`
   - `GET /conversations` → `[ conversations ]`
   - `GET /conversations/{id}` → `{ conversation }`
   - `GET /documents` → `[ documents ]`
   - `POST /documents` → `multipart/form-data`
   - `DELETE /documents/{id}` → `{ success: true }`
   - `GET /admin/stats` → `{ documents, indexed, chunks, errors }`
