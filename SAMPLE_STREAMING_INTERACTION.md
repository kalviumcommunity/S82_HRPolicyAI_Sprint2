# HRPolicyAI — Progressive Answer Streaming & Citations Log

This document records the verification and sample interaction logs for progressive streaming answers and interactive citations (`[1]`, `[2]`), fulfilling Tasks 1 through 5.

---

## Task 1: Progressive Answer Streaming Flow

When a user submits an HR policy query, the answer is streamed progressively word-by-word/token-by-token instead of blocking until completion.

### Timeline of a Progressive Stream Event:
1. **t = 0 ms**: User submits prompt:  
   `"How many annual leave days can I take in the India office?"`  
   - UI immediately creates an optimistic user message and mounts an assistant container in `isStreaming: true` state.
   - Status bar indicates: `Searching ChromaDB vector index & extracting policy chunks...`
   - Active `AbortController` is attached.

2. **t = 50 ms — Event: `sources`**:
   - Backend sends Server-Sent Events (SSE) metadata payload with retrieved policy sources:
     ```json
     event: sources
     data: {
       "conversation_id": "conv_01",
       "message_id": "msg_a_98f12a",
       "sources": [
         {
           "document_id": "doc_in_leave",
           "chunk_id": "chk_in_leave_041",
           "marker": "[1]",
           "citation_index": 1,
           "document": "India Leave Policy 2026",
           "section": "Section 4.1: Annual Leave Entitlement",
           "page": 7,
           "score": 0.97
         },
         {
           "document_id": "doc_gl_handbook",
           "chunk_id": "chk_gl_handbook_112",
           "marker": "[2]",
           "citation_index": 2,
           "document": "Global Employee Handbook",
           "section": "Chapter 5: Statutory Leaves & Holidays",
           "page": 34,
           "score": 0.89
         }
       ]
     }
     ```
   - Citation source cards are rendered dynamically under the message.

3. **t = 80 ms — t = 600 ms — Event: `token`**:
   - Words stream progressively into the active chat bubble with pulsing cursor `▋`:
     - *Chunk 1*: `"Employees "`
     - *Chunk 2*: `"in India "`
     - *Chunk 3*: `"are entitled to 18 days of paid annual leave "`
     - *Chunk 4*: `"per calendar year [1], "`
     - *Chunk 5*: `"accrued at 1.5 days per month. In addition, employees receive 12 days of sick/casual leave and 10 declared public holidays [2]. "`
     - *Chunk 6*: `"Carry-over is capped at 8 days annually [1]."`

4. **t = 650 ms — Event: `done`**:
   - Backend signals stream completion.
   - Assistant message is marked `isStreaming: false`, removing the cursor indicator and finalizing the consultation record.

---

## Task 2: Inline Citations & Source Markers

### Inline Citation Rendering:
* The answer text embeds interactive citation markers like `[1]` and `[2]`.
* Each marker is rendered as a distinct pill button:
  - **Color**: Blue-tinted badge with border and hover zoom effect.
  - **Tooltip**: Displays `"Click to view Source [1] citation excerpt"`.
  - **Action**: Clicking `[1]` directly opens the modal for the corresponding document and chunk.

### Citation Cards Below Answer:
Each source is listed with:
1. **Citation Index Badge**: `[1]` / `[2]`
2. **Document Name**: `India Leave Policy 2026`
3. **Chunk ID Tag**: `#chk_in_leave_041`
4. **Section & Page**: `Section 4.1: Annual Leave Entitlement · Page 7`
5. **Relevance Match**: `97% Match`
6. **Jurisdiction & Version**: `India · v2026.1`

---

## Task 3: Viewing Cited Sources & Excerpts

Users can inspect the full grounded source excerpt in two ways:
1. **Clicking the Inline Citation Marker**: Clicking `[1]` in the text immediately opens the modal for Chunk `chk_in_leave_041`.
2. **Clicking "View Source Excerpt & Context"**: Opens the citation modal displaying:
   - Full verbatim chunk text formatted with quotation marks.
   - Copyable Chunk ID (`#chk_in_leave_041`) with copy feedback.
   - "Copy excerpt" button with toast confirmation.
   - Policy metadata grid (document, section, page, jurisdiction, score).

---

## Task 4: Streaming Interruption & Error Resilience

1. **Stop Generation Button**:
   - While streaming is active, a prominent **"Stop Generating Response"** button appears above the input bar and inside the composer.
   - Clicking it triggers `abortController.abort()`, safely halting the stream without freezing the UI or corrupting conversation history.

2. **Network Timeout / Interruption Recovery**:
   - If a stream disconnects or the backend returns an error:
     - Error banner appears: `Query Failed: Connection interrupted while streaming response.`
     - **"Retry"** button re-executes the prompt immediately.
     - Prior conversation history and partial content remain accessible.

---

## Task 5: Verification Summary

| Feature | Description | Status |
| :--- | :--- | :--- |
| **SSE Streaming Backend** | `POST /chat/stream` emits `sources`, `token`, `done`, and `error` events | Verified |
| **Progressive UI Streaming** | Word-by-word streaming animation with pulsing cursor `▋` | Verified |
| **Inline `[1]` Markers** | Interactive pill markers parsed and linked to source cards | Verified |
| **Source Excerpt Modal** | Verbatim chunk display, Chunk ID copying, metadata grid | Verified |
| **Stream Cancellation** | `AbortController` stop button halts generation cleanly | Verified |
| **Error Handling** | Dismissible alert with retry capability on stream drop | Verified |
| **Vite Production Build** | Compiled cleanly without warnings or errors | Verified |
