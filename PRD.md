# Product Requirements Document (PRD)
## HRPolicyAI — AI-Powered HR Policy Assistant

| Field | Details |
|---|---|
| Version | 1.0.0 |
| Status | In Development |
| Document Type | Product Requirements Document |
| Project | HRPolicyAI |
| Tech Stack | React.js · Vite · Tailwind CSS · Python · FastAPI · LangChain · OpenAI API · OpenAI Embeddings · ChromaDB · MongoDB · Git · GitHub |

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Business Problem](#2-business-problem)
3. [User Personas](#3-user-personas)
4. [User Pain Points](#4-user-pain-points)
5. [Project Goals](#5-project-goals)
6. [Technology Stack](#6-technology-stack)
7. [Functional Requirements](#7-functional-requirements)
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [User Stories](#9-user-stories)
10. [MVP Scope](#10-mvp-scope)
11. [Future Scope](#11-future-scope)
12. [Risks and Assumptions](#12-risks-and-assumptions)
13. [Acceptance Criteria](#13-acceptance-criteria)
14. [Team Responsibilities](#14-team-responsibilities)

---

## 1. Executive Summary

HRPolicyAI is an AI-powered HR policy assistant designed to reduce repetitive HR queries by allowing employees to ask questions in natural language.

The application uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from official HR documents before generating an answer. The system works with documents such as:

- Employee handbooks
- Leave policies
- Benefits policies
- Insurance policies
- Holiday policies
- Work-from-home policies
- Regional HR policies

Because HR policies can differ between regions, documents are stored with relevant metadata such as region, policy category, and document version. The system retrieves the appropriate information and provides the employee with:

- A direct answer
- Relevant policy information
- Source document
- Page/source reference
- A safe response when sufficient information cannot be found

The primary objective is to provide fast, reliable, and document-grounded HR answers without replacing the HR department.

---

## 2. Business Problem

### 2.1 Context

HR departments maintain large amounts of policy documentation. Employees often need information about policies but may not know where to find the correct document or section.

Common questions include:
- "How many annual leaves do I get?"
- "Can I carry forward unused leaves?"
- "What medical benefits are available?"
- "What is the parental leave policy?"
- "Does this policy apply to employees in India?"
- "What is the notice period?"

### 2.2 Core Gap

The current process requires employees to manually search through documents or contact HR. HRPolicyAI solves this by creating an AI-based search and question-answering layer over existing HR documentation.

### 2.3 Business Impact

- HR teams spend time answering repetitive questions
- Employees wait for answers to simple policy questions
- Employees may read outdated or incorrect policy documents
- Region-specific policies can easily be confused
- HR teams have less time for complex employee issues

---

## 3. User Personas

### 3.1 Persona 1 — Employee
| | |
|---|---|
| **Role** | Company Employee |
| **Goal** | Get quick answers to HR-related questions |
| **Frustration** | Has to search through long documents or contact HR for simple questions |
| **Success** | Gets a clear answer with the relevant official source |

### 3.2 Persona 2 — HR Administrator
| | |
|---|---|
| **Role** | HR Team Member |
| **Goal** | Maintain accurate and up-to-date HR documentation |
| **Frustration** | Receives repetitive questions already answered in company policies |
| **Success** | Employees can independently find answers to common questions |

### 3.3 Persona 3 — HR Manager
| | |
|---|---|
| **Role** | HR Manager |
| **Goal** | Monitor policy information and ensure employees receive accurate information |
| **Frustration** | Difficulty maintaining consistency when policies differ across regions |
| **Success** | Employees receive answers based on the correct regional and current policy |

---

## 4. User Pain Points

| # | User | Pain Point | Severity |
|---|---|---|---|
| P1 | Employee | Cannot quickly find answers inside lengthy HR documents | Critical |
| P2 | Employee | Has to contact HR for repetitive questions | Critical |
| P3 | Employee | May accidentally use an outdated policy | High |
| P4 | Employee | Regional differences make policies confusing | Critical |
| P5 | HR | Spends time answering repetitive questions | Critical |
| P6 | HR | Managing multiple policy documents is difficult | High |
| P7 | HR | Employees may misunderstand policy wording | High |
| P8 | HR Manager | Difficult to ensure answers are based on official sources | Critical |

---

## 5. Project Goals

| Goal | Description |
|---|---|
| G1 — Reduce Repetitive HR Queries | Allow employees to independently answer common HR questions |
| G2 — Provide Grounded Answers | Generate answers using official HR documents |
| G3 — Support Regional Policies | Retrieve policies based on employee region |
| G4 — Provide Source Citations | Show employees where the answer came from |
| G5 — Prevent Hallucinations | Refuse to answer when sufficient information cannot be retrieved |
| G6 — Centralize HR Knowledge | Provide one interface for accessing HR policies |

---

## 6. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React.js | Build the employee and HR interfaces |
| Build Tool | Vite | Frontend development and build |
| Styling | Tailwind CSS | Responsive UI design |
| Backend | FastAPI | Build APIs and backend services |
| Language | Python | RAG and backend development |
| LLM | OpenAI API | Generate natural-language answers |
| RAG Framework | LangChain | Connect retrieval and generation components |
| Embeddings | OpenAI Embeddings | Convert documents and queries into vectors |
| Vector Database | ChromaDB | Store and retrieve document embeddings |
| Database | MongoDB | Store users, documents, conversations and metadata |
| Document Processing | pdfplumber | Extract text from PDF documents |
| Authentication | JWT | Secure user authentication |
| API Communication | Axios | Frontend-backend communication |
| Version Control | Git & GitHub | Source control and collaboration |
| Frontend Deployment | Vercel | Deploy frontend |
| Backend Deployment | Render | Deploy backend |

---

## 7. Functional Requirements

### 7.1 User Authentication

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | System SHALL allow employees to log in securely | Must Have |
| FR-02 | System SHALL authenticate users using JWT | Must Have |
| FR-03 | System SHALL associate employees with their region | Must Have |
| FR-04 | System SHALL provide different access levels for employees and HR administrators | Should Have |

### 7.2 Document Management

| ID | Requirement | Priority |
|---|---|---|
| FR-05 | HR administrators SHALL be able to upload HR documents | Must Have |
| FR-06 | System SHALL extract text from uploaded PDF documents | Must Have |
| FR-07 | System SHALL clean extracted document text | Must Have |
| FR-08 | System SHALL divide documents into retrievable chunks | Must Have |
| FR-09 | System SHALL attach metadata such as region, category and document version | Must Have |
| FR-10 | System SHALL generate embeddings for document chunks | Must Have |
| FR-11 | System SHALL store embeddings in ChromaDB | Must Have |

### 7.3 Question Answering

| ID | Requirement | Priority |
|---|---|---|
| FR-12 | Employee SHALL be able to ask questions using natural language | Must Have |
| FR-13 | System SHALL convert the question into an embedding | Must Have |
| FR-14 | System SHALL retrieve relevant document chunks | Must Have |
| FR-15 | System SHALL filter results based on employee region when applicable | Must Have |
| FR-16 | System SHALL provide retrieved context to the LLM | Must Have |
| FR-17 | System SHALL generate an answer based on retrieved information | Must Have |
| FR-18 | System SHALL display relevant source documents | Must Have |
| FR-19 | System SHALL refuse to provide unsupported answers | Must Have |

### 7.4 Conversational Interaction

| ID | Requirement | Priority |
|---|---|---|
| FR-20 | System SHALL maintain conversation history | Should Have |
| FR-21 | System SHALL support follow-up questions | Should Have |
| FR-22 | System SHALL use previous conversation context when required | Should Have |
| FR-23 | System SHALL allow users to start a new conversation | Must Have |

### 7.5 HR Dashboard

| ID | Requirement | Priority |
|---|---|---|
| FR-24 | HR administrators SHALL be able to view uploaded documents | Must Have |
| FR-25 | HR administrators SHALL be able to view document status | Must Have |
| FR-26 | HR administrators SHALL be able to upload updated policy versions | Must Have |
| FR-27 | System SHALL maintain document metadata | Must Have |

---

## 8. Non-Functional Requirements

### 8.1 Performance
| ID | Requirement |
|---|---|
| NFR-01 | Normal user queries should return an answer within a reasonable response time |
| NFR-02 | Document retrieval should return the most relevant chunks efficiently |
| NFR-03 | UI should remain responsive while the AI is processing a request |

### 8.2 Security
| ID | Requirement |
|---|---|
| NFR-04 | API keys SHALL never be stored in source code |
| NFR-05 | Sensitive configuration SHALL be stored using environment variables |
| NFR-06 | User authentication SHALL be secured |
| NFR-07 | Employees SHALL only access information permitted for their role |

### 8.3 Reliability
| ID | Requirement |
|---|---|
| NFR-08 | System SHALL handle unavailable or malformed documents gracefully |
| NFR-09 | System SHALL provide meaningful error messages |
| NFR-10 | Failed document indexing SHALL not silently pass as successful |

### 8.4 Maintainability
| ID | Requirement |
|---|---|
| NFR-11 | Code SHALL be organized into reusable components |
| NFR-12 | Dependencies SHALL be documented |
| NFR-13 | GitHub SHALL be used for version control |
| NFR-14 | Project setup instructions SHALL be included in README.md |

---

## 9. User Stories

### US-101 — Ask HR Question
> As an employee, I want to ask questions about HR policies in natural language so that I can quickly find the information I need.

**Acceptance Criteria:**
- Employee can enter a question
- System searches relevant HR documents
- System returns a clear answer
- Answer is based on retrieved policy information

### US-102 — Region-Specific Answer
> As an employee, I want the system to consider my region so that I receive the correct regional policy.

**Acceptance Criteria:**
- Employee has an associated region
- Retrieval considers region metadata
- Regional policy is prioritized when applicable
- System does not incorrectly combine conflicting regional policies

### US-103 — Source Verification
> As an employee, I want to see the source of an answer so that I can verify the information.

**Acceptance Criteria:**
- AI response displays the source document
- Relevant page or section is displayed where available
- User can identify which policy supports the answer

### US-104 — Safe Refusal
> As an employee, I want the AI to admit when information is unavailable so that I do not receive a fabricated HR answer.

**Acceptance Criteria:**
- System checks whether relevant information was retrieved
- If sufficient information is unavailable, system does not invent an answer
- System recommends contacting HR when appropriate

### US-105 — Upload Policy
> As an HR administrator, I want to upload new policy documents so that the AI knowledge base stays updated.

**Acceptance Criteria:**
- HR can upload a document
- System extracts and processes the content
- Document is chunked and embedded
- Document is added to the vector database
- Document metadata is stored

---

## 10. MVP Scope

### Included in MVP

| Feature | Purpose |
|---|---|
| Employee Login | Secure application access |
| AI Chat Interface | Ask HR questions |
| PDF Upload | Add HR policies |
| Text Extraction | Extract policy content |
| Document Chunking | Prepare content for retrieval |
| Embeddings | Convert content into vectors |
| ChromaDB | Store and search embeddings |
| Semantic Search | Find relevant policy information |
| Region Filtering | Retrieve appropriate regional policies |
| LLM Answer Generation | Generate natural-language responses |
| Source Citations | Allow answer verification |
| Hallucination Handling | Prevent unsupported answers |
| Conversation History | Maintain previous questions |
| HR Document Dashboard | Manage uploaded policies |

### Excluded from MVP

- Voice-based HR assistant
- WhatsApp / Slack / Email integration
- Automatic policy approval or HR decision-making
- Payroll processing, performance management, or direct modification of employee records

---

## 11. Future Scope

### Phase 2 — Advanced AI
- Multi-language HR support
- Improved conversational memory
- Advanced document re-ranking
- Automatic policy conflict detection
- AI-generated policy summaries

### Phase 3 — Enterprise Integrations
- Slack & Microsoft Teams integration
- HRMS integration, Email integration
- SSO authentication, Advanced role-based access control

### Phase 4 — Advanced HR Intelligence
- HR query analytics, FAQ detection
- Policy gap identification
- Automatic alerts when policies expire
- Policy version comparison

---

## 12. Risks and Assumptions

### Risks

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | AI generates unsupported information | High | Use grounded RAG and refusal handling |
| R2 | Incorrect regional policy is retrieved | High | Use region metadata filtering |
| R3 | Poor document chunking reduces retrieval quality | High | Test and tune chunking strategy |
| R4 | Outdated documents produce outdated answers | High | Maintain document versions and effective dates |
| R5 | Poor-quality source documents affect answers | Medium | Validate documents during ingestion |
| R6 | API costs increase with heavy usage | Medium | Caching and usage monitoring |
| R7 | Sensitive HR information is exposed | High | Authentication and access control |

### Assumptions

| # | Assumption |
|---|---|
| A1 | HR policies are available as digital documents |
| A2 | PDF is the primary document format for the MVP |
| A3 | Documents contain enough information to answer common employee questions |
| A4 | Each document can be associated with a region and category |
| A5 | OpenAI API access is available |
| A6 | The application is initially intended as an internal HR assistant |

---

## 13. Acceptance Criteria

### AC-1 — Document Processing
- HR administrator can upload an HR document
- Text is extracted successfully; document is cleaned and chunked
- Chunks contain required metadata; embeddings stored in ChromaDB

### AC-2 — Retrieval
- Employee questions are converted into embeddings
- Relevant document chunks are retrieved with region filtering
- Retrieved chunks contain source information

### AC-3 — Answer Generation
- AI generates answers using retrieved context
- Answers remain grounded; unsupported questions result in a safe response
- Answers display their source

### AC-4 — User Interface
- Employee can log in, ask questions, view responses, view citations, access conversation history
- HR administrator can upload and manage documents

### AC-5 — Security
- API keys stored securely via environment variables
- Authentication implemented; employee and HR permissions separated
- Sensitive configuration not committed to GitHub

---

## 14. Team Responsibilities

### Member 1 — Frontend & UI
- React.js application, Login/signup UI, Employee dashboard
- AI chat interface, Conversation history, Source citation UI
- HR admin dashboard, Document upload UI, Responsive design, API integration

### Member 2 — Backend & Database
- FastAPI backend, REST APIs, JWT authentication
- MongoDB integration, User/document/conversation management
- Document upload API, Error handling, Backend deployment

### Member 3 — AI / RAG
- Document processing pipeline: PDF extraction, text cleaning, chunking, metadata
- OpenAI embeddings, ChromaDB setup, semantic similarity search, region-based retrieval
- RAG pipeline, LLM integration, grounded answer generation
- Source citations, hallucination/refusal handling, RAG evaluation

---

## Project Architecture

```
                    HR Documents
                         |
                         v
                Document Processing
                         |
              +----------+-----------+
              v                      v
          Chunking               Metadata
              |                  Region/Type
              v
        Embedding Model
              |
              v
          ChromaDB
              |
Employee --> Question
              |
              v
        Query Embedding
              |
              v
       Similarity Search
              |
       Region Filtering
              |
              v
       Relevant Chunks
              |
              v
        OpenAI LLM
              |
              v
       Grounded Answer
              |
              v
     Answer + Source Citation
```
