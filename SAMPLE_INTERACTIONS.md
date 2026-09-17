# HRPolicyAI — Sample Interactions & UI Verification Log

This document provides sample interactions demonstrating the full functionality of the HRPolicyAI Retrieval-Augmented Generation (RAG) assistant UI, fulfilling Tasks 1 through 5.

---

## Task 1 & 2: Question and Answer UI & Backend RAG API Integration

### Sample Interaction 1: Annual Leave Entitlements
* **User Input Question**:  
  > `"How many annual leave days can I take in the India office?"`
* **API Endpoint**: `POST /chat`  
* **Request Payload**:
  ```json
  {
    "conversation_id": "conv_01",
    "question": "How many annual leave days can I take in the India office?"
  }
  ```
* **Response Payload**:
  ```json
  {
    "conversation_id": "conv_01",
    "message_id": "msg_01_ai",
    "answer": "Under the official India Leave Policy 2026, full-time employees are entitled to 18 days of paid annual leave per calendar year. Leaves accrue at a rate of 1.5 days per completed month of service.\n\nKey guidelines:\n• Annual leave must be requested at least 7 working days in advance for absences over 3 consecutive days.\n• Up to 8 unused annual leave days can be carried forward into the next calendar year; any excess beyond 8 days will lapse on December 31st.\n• Annual leave can be clubbed with weekend holidays but cannot be combined with sick leave without medical certificate.",
    "sources": [
      {
        "document_id": "doc_in_leave",
        "chunk_id": "chk_in_leave_041",
        "document": "India Leave Policy 2026",
        "section": "Section 4.1: Annual Leave Entitlement",
        "page": 7,
        "region": "India",
        "version": "2026.1",
        "score": 0.96,
        "excerpt": "Employees are entitled to 18 days of paid annual leave per calendar year, accrued monthly at 1.5 days per completed calendar month of active service. A maximum carry-over of 8 days into the subsequent year is permitted."
      },
      {
        "document_id": "doc_gl_handbook",
        "chunk_id": "chk_gl_handbook_112",
        "document": "Global Employee Handbook",
        "section": "Chapter 5: Time Off & Attendance",
        "page": 32,
        "region": "Global",
        "version": "2026.2",
        "score": 0.88,
        "excerpt": "Statutory leave entitlements are governed by country-specific addenda. Where local law or policy offers greater benefits, the regional annexure supersedes general corporate guidelines."
      }
    ]
  }
  ```
* **UI Display**:
  - Grounded answer displayed with formatting and bullet points.
  - "Grounded in Policy" badge with shield icon.
  - One-click copy answer button and feedback thumbs up/down actions.

---

## Task 3: Retrieved Sources & Chunk Metadata Display

### Sample Interaction 2: Group Mediclaim & Health Insurance
* **User Input Question**:  
  > `"Does our health insurance cover dependent parents in India?"`
* **Grounded Answer**:
  > `"Yes, under the 2026 Group Mediclaim (GMC) Policy in India, dependent parents (or parents-in-law, up to 2 individuals) can be enrolled during the annual flex benefits window in January or within 30 days of marriage/joining.\n\n• Base Coverage: ₹5,00,000 corporate floater for employee + spouse + up to 2 children.\n• Parental Top-Up: Optional parental cover available from ₹3,00,000 to ₹10,00,000 with corporate co-pay subsidy.\n• Cashless Hospitalization: Available across 8,500+ network hospitals via the TPA portal."`
* **Retrieved Source Cards Displayed**:
  1. **Source Card 1**:
     - **Document**: `India Group Health Insurance Coverage`
     - **Chunk ID**: `#chk_in_insurance_089`
     - **Section**: `Annexure B: Dependent Enrolment & Parental Add-on (Page 12)`
     - **Jurisdiction & Version**: `India · v2026.1`
     - **Relevance Match**: `95% Match`
     - **Action**: Clicking "View Source Excerpt & Context" opens the citation modal.
  2. **Citation Modal Details**:
     - Direct verbatim quote excerpt formatted with quote styling.
     - Copyable Chunk ID (`#chk_in_insurance_089`) with copy feedback.
     - Copy excerpt button with toast confirmation.
     - Vector store grounding confirmation banner.

---

## Task 4: Loading & Error States

### 1. Multi-Stage Loading State
When a question is submitted:
1. **Stage 1 (0ms - 450ms)**:  
   - Spinner icon rotates.
   - Status badge shows: `Searching ChromaDB vector index...`
   - Subtitle indicates: `Retrieving chunks from vector store & preparing cited response...`
2. **Stage 2 (450ms - 900ms)**:  
   - Status transitions to: `Retrieving relevant policy chunks & citations...`
3. **Stage 3 (900ms+)**:  
   - Status transitions to: `Synthesizing grounded response with citations...`
   - Input field and send button are disabled to prevent duplicate submissions.

### 2. Error State & Graceful Recovery
When network connectivity is lost or backend throws an exception:
* **Error Banner**:
  - Displays inline alert with warning icon: `Query Failed: Request failed with status 500 / Network Error`
  - Shows **"Retry"** button which automatically re-executes the last failed prompt without retyping.
  - Shows **"Dismiss"** button to clear the error banner.
  - Preserves prior conversation history without data corruption.

---

## Task 5: Summary of Implemented Features

| Feature Area | Implementation Details | Status |
| :--- | :--- | :--- |
| **Q&A Input Interface** | Auto-resizing textarea, Enter to submit, Shift+Enter newline, suggestion chips | Verified |
| **RAG Backend API** | Connects to FastAPI endpoint `POST /chat` with query payload & conversation tracking | Verified |
| **Source Citations** | Document name, chunk ID (`#chk_...`), section, page, version, match score, excerpt modal | Verified |
| **Loading States** | Multi-phase status feedback, animated indicators, disabled form controls | Verified |
| **Error Handling** | Dismissible error banner, automatic retry button, failed request resilience | Verified |
| **Build & Compatibility** | Clean Vite build (`npm run build`) without errors | Verified |
