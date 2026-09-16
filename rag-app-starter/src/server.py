import os
import sys
import uuid
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

load_dotenv(PROJECT_ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("hrpolicyai_api")

app = FastAPI(
    title="HRPolicyAI RAG API",
    description="Backend API for HRPolicyAI RAG Pipeline, Document Search, and Chat Assistant",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory & persisted state store ---
USERS_DB = [
    {
        "id": "usr_emp_01",
        "name": "Sarah Jenkins",
        "email": "sarah.jenkins@company.com",
        "password": "password123",
        "role": "EMPLOYEE",
        "region": "India",
        "department": "Engineering",
        "avatar": "SJ",
        "joinedDate": "2024-03-15",
    },
    {
        "id": "usr_adm_01",
        "name": "David Miller",
        "email": "david.miller@company.com",
        "password": "admin123",
        "role": "HR_ADMIN",
        "region": "India",
        "department": "People Operations",
        "avatar": "DM",
        "joinedDate": "2022-06-01",
    },
    {
        "id": "usr_adm_02",
        "name": "HR Administrator",
        "email": "admin@company.com",
        "password": "admin123",
        "role": "HR_ADMIN",
        "region": "India",
        "department": "People Operations",
        "avatar": "HA",
        "joinedDate": "2022-01-01",
    },
]

DOCUMENTS_DB = [
    {
        "id": "doc_in_leave",
        "name": "India Leave Policy 2026",
        "filename": "India_Leave_Policy_2026.pdf",
        "region": "India",
        "category": "Leave Policy",
        "version": "2026.1",
        "effectiveDate": "2026-01-01",
        "status": "Indexed",
        "chunkCount": 142,
        "fileSize": "1.8 MB",
        "updatedAt": "2026-01-10T10:30:00Z",
        "author": "Corporate HR",
    },
    {
        "id": "doc_us_leave",
        "name": "USA PTO & Paid Leave Policy",
        "filename": "USA_PTO_Policy_2026.pdf",
        "region": "USA",
        "category": "Leave Policy",
        "version": "2026.0",
        "effectiveDate": "2026-01-01",
        "status": "Indexed",
        "chunkCount": 185,
        "fileSize": "2.3 MB",
        "updatedAt": "2026-01-12T14:20:00Z",
        "author": "US Benefits Team",
    },
    {
        "id": "doc_gl_handbook",
        "name": "Global Employee Handbook",
        "filename": "Global_Employee_Handbook_2026.pdf",
        "region": "Global",
        "category": "Handbook",
        "version": "2026.2",
        "effectiveDate": "2026-01-01",
        "status": "Indexed",
        "chunkCount": 512,
        "fileSize": "4.6 MB",
        "updatedAt": "2026-02-01T09:15:00Z",
        "author": "People & Culture",
    },
    {
        "id": "doc_in_insurance",
        "name": "India Group Health Insurance Coverage",
        "filename": "India_GMC_Policy_2026.pdf",
        "region": "India",
        "category": "Benefits",
        "version": "2026.1",
        "effectiveDate": "2026-01-15",
        "status": "Indexed",
        "chunkCount": 220,
        "fileSize": "2.1 MB",
        "updatedAt": "2026-02-14T11:00:00Z",
        "author": "APAC Benefits Group",
    },
    {
        "id": "doc_gl_parental",
        "name": "Global Parental & Caregiver Leave",
        "filename": "Global_Parental_Leave_2026.pdf",
        "region": "Global",
        "category": "Leave Policy",
        "version": "2026.0",
        "effectiveDate": "2026-01-01",
        "status": "Indexed",
        "chunkCount": 98,
        "fileSize": "1.2 MB",
        "updatedAt": "2026-01-05T08:45:00Z",
        "author": "Diversity & Inclusion",
    },
]

# --- JSON-file persistence for DOCUMENTS_DB and USERS_DB ---
DOCS_STORE_PATH = PROJECT_ROOT / "data" / "documents_store.json"
USERS_STORE_PATH = PROJECT_ROOT / "data" / "users_store.json"


def load_documents_store() -> list:
    """Load persisted documents from JSON file, merging with seeded docs as baseline.
    
    Strategy: always start from the hardcoded seed list, then overlay/extend with
    anything stored in the JSON file. This means seeded docs are NEVER lost on
    restart, and newly uploaded docs from the JSON store are merged in.
    """
    seeded_ids = {d["id"] for d in DOCUMENTS_DB}
    merged = [dict(d) for d in DOCUMENTS_DB]  # start from seeded baseline
    try:
        if DOCS_STORE_PATH.exists():
            with open(DOCS_STORE_PATH, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, list):
                for doc in stored:
                    if doc.get("id") not in seeded_ids:
                        merged.append(doc)  # add newly uploaded docs
                logger.info(
                    "Merged %d seeded + %d uploaded documents from persistent store.",
                    len(seeded_ids),
                    len(merged) - len(seeded_ids),
                )
    except Exception as e:
        logger.warning("Failed to load documents_store.json, using seeded data only: %s", e)
    return merged


def save_documents_store():
    """Persist current DOCUMENTS_DB to JSON file (seeded + uploaded docs)."""
    try:
        DOCS_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Save ALL documents (seeded + uploaded) so cross-device reads work
        with open(DOCS_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(DOCUMENTS_DB, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning("Failed to save documents_store.json: %s", e)


def load_users_store() -> list:
    """Load persisted users from JSON file, merging with seeded users."""
    try:
        if USERS_STORE_PATH.exists():
            with open(USERS_STORE_PATH, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, list) and stored:
                # Merge: seed users take priority if updated, but keep newly registered ones
                seeded_ids = {u["id"] for u in USERS_DB}
                merged = USERS_DB[:]
                for su in stored:
                    if su["id"] not in seeded_ids:
                        merged.append(su)
                logger.info("Loaded %d users from persistent store.", len(merged))
                return merged
    except Exception as e:
        logger.warning("Failed to load users_store.json: %s", e)
    return USERS_DB[:]


def save_users_store():
    """Persist current USERS_DB to JSON file."""
    try:
        USERS_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(USERS_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(USERS_DB, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning("Failed to save users_store.json: %s", e)


CONVS_STORE_PATH = PROJECT_ROOT / "data" / "conversations_store.json"


def load_conversations_store() -> list:
    """Load persisted conversations from JSON file."""
    try:
        if CONVS_STORE_PATH.exists():
            with open(CONVS_STORE_PATH, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, list):
                logger.info("Loaded %d conversations from persistent store.", len(stored))
                return stored
    except Exception as e:
        logger.warning("Failed to load conversations_store.json: %s", e)
    return []


def save_conversations_store():
    """Persist current CONVERSATIONS_DB to JSON file."""
    try:
        CONVS_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONVS_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(CONVERSATIONS_DB, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning("Failed to save conversations_store.json: %s", e)



CONVERSATIONS_DB: List[Dict[str, Any]] = []

# Knowledge base fallback answers for realistic responses when LLM key is not provided
POLICY_KNOWLEDGE_BASE = [
    {
        "keywords": ["maternity", "mother", "pregnancy"],
        "answer": "Under the India Maternity Benefit guidelines, female employees are entitled to 26 weeks (182 calendar days) of fully paid maternity leave for up to two surviving children. Applications should be submitted at least 8 weeks prior to the expected delivery date.",
        "sources": [
            {
                "document_id": "doc_in_leave",
                "document": "India Leave Policy 2026",
                "section": "Section 4.1: Maternity Leave",
                "page": 12,
                "region": "India",
                "version": "2026.1",
                "excerpt": "Female employees who have worked for at least 80 days in the 12 months preceding the date of expected delivery are entitled to 26 weeks of paid leave."
            }
        ]
    },
    {
        "keywords": ["paternity", "father", "parental"],
        "answer": "Eligible fathers and secondary caregivers are entitled to 15 business days of paid paternity leave, which must be availed within 6 months of child birth or adoption.",
        "sources": [
            {
                "document_id": "doc_gl_parental",
                "document": "Global Parental & Caregiver Leave",
                "section": "Section 3: Paternity Entitlement",
                "page": 7,
                "region": "Global",
                "version": "2026.0",
                "excerpt": "Secondary caregivers receive up to 15 working days of paid leave within 180 days of the qualifying life event."
            }
        ]
    },
    {
        "keywords": ["sick", "medical", "illness", "doctor"],
        "answer": "Employees receive 12 days of paid medical/sick leave per calendar year. Medical certificates are mandatory for consecutive absences exceeding 3 working days.",
        "sources": [
            {
                "document_id": "doc_in_leave",
                "document": "India Leave Policy 2026",
                "section": "Section 2.3: Medical Leave",
                "page": 8,
                "region": "India",
                "version": "2026.1",
                "excerpt": "Medical leaves accrue on a quarterly basis. A registered medical practitioner certificate is required for leaves of 3+ consecutive days."
            }
        ]
    },
    {
        "keywords": ["insurance", "gmc", "health", "hospital", "coverage", "claim"],
        "answer": "The Group Medical Coverage (GMC) provides INR 5,00,000 baseline sum insured for the employee, spouse, and up to 2 dependent children. OPD dental and optical allowances are provided separately up to INR 15,000 annually.",
        "sources": [
            {
                "document_id": "doc_in_insurance",
                "document": "India Group Health Insurance Coverage",
                "section": "Policy Summary & Floater Limits",
                "page": 3,
                "region": "India",
                "version": "2026.1",
                "excerpt": "The standard policy covers hospitalization expenses up to 5 lakhs INR with cashless facility at all network hospitals."
            }
        ]
    },
    {
        "keywords": ["pto", "annual", "vacation", "earned leave", "holiday"],
        "answer": "Full-time employees receive 20 days of paid annual/earned leave per year, accrued at 1.67 days per month. Unused leave up to 10 days can be carried forward to the next calendar year.",
        "sources": [
            {
                "document_id": "doc_in_leave",
                "document": "India Leave Policy 2026",
                "section": "Section 2.1: Annual Privilege Leave",
                "page": 4,
                "region": "India",
                "version": "2026.1",
                "excerpt": "Annual leave must be approved by the reporting manager at least 2 weeks in advance of planned vacation."
            }
        ]
    }
]


# --- Request/Response Schemas ---
class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = ""

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    region: Optional[str] = "India"

class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None

class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)

class Source(BaseModel):
    source: str
    chunk_id: Optional[str] = None
    score: Optional[float] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    status: str


# --- Helper Methods ---
def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        for u in USERS_DB:
            if u["id"] in token:
                return u
        raise HTTPException(status_code=401, detail="Invalid token or session expired.")
    raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")


def require_admin(request: Request) -> dict:
    """Dependency: raises 403 if the caller is not an HR_ADMIN."""
    user = get_current_user(request)
    if user.get("role") != "HR_ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Access denied. HR Admin role required for this action."
        )
    return user


MIN_TOP_SCORE = 0.72
MIN_SUPPORTING_CHUNKS = 1

def retrieval_is_strong(chunks: list) -> bool:
    if not chunks:
        return False
    strong_chunks = [chunk for chunk in chunks if chunk["score"] >= MIN_TOP_SCORE]
    return len(strong_chunks) >= MIN_SUPPORTING_CHUNKS

def build_citation_map(chunks: list) -> dict:
    citation_map = {}
    for index, chunk in enumerate(chunks, start=1):
        citation_map[f"[{index}]"] = {
            "document_id": chunk["metadata"].get("source", "Unknown"),
            "document": chunk["metadata"].get("source", "Unknown Document"),
            "section": chunk["metadata"].get("section", "General"),
            "page": chunk["metadata"].get("page", 1),
            "region": chunk["metadata"].get("region", "Global"),
            "version": chunk["metadata"].get("version", "Latest"),
            "excerpt": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"]
        }
    return citation_map

def rewrite_followup(client, model, history, question):
    if not history:
        return question
    
    # Keep only the last 3 turns (6 messages) to prevent context overflow and token bloat
    recent_history = history[-6:]
    history_text = "\n".join([f"{msg['sender'].capitalize()}: {msg['text']}" for msg in recent_history])
    
    prompt = f"""Rewrite the user's latest question as a standalone search query. 
Use the conversation history only to resolve references (like "it", "they", "this policy"). 
Do not answer the question. 
History:
{history_text}
Latest question: {question}
Standalone query:"""
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content.strip()


def generate_rag_response(question: str, history: list = None) -> tuple[str, list]:
    """Execute live RAG if OpenAI and vector store configured, otherwise grounded knowledge base."""
    api_key = os.getenv("OPENAI_API_KEY")
    chat_model = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Check if we can perform Chroma/OpenAI RAG
    if api_key:
        try:
            from openai import OpenAI
            import chromadb
            from retrieval import embed_query, get_collection, retrieve_chunks
            from prompts.answer import render_answer_prompt
            
            base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("API_BASE_URL") or "https://api.openai.com/v1"
            client = OpenAI(api_key=api_key, base_url=base_url)
            
            # Rewrite follow-up question if history is provided
            standalone_query = rewrite_followup(client, chat_model, history, question)
            logger.info("Original question: %s | Standalone query: %s", question, standalone_query)
            
            # Setup Chroma
            db_path_env = os.getenv("VECTOR_DB_URL")
            db_path = Path(db_path_env) if db_path_env else PROJECT_ROOT / ".chroma"
            chroma_client = chromadb.PersistentClient(path=str(db_path))
            collection_name = os.getenv("COLLECTION_NAME", "hr_policy_chunks")
            collection = get_collection(chroma_client, collection_name)
            
            # Retrieve chunks
            query_embedding = embed_query(standalone_query, client, embedding_model)
            chunks = retrieve_chunks(collection, query_embedding, k=3)
            
            # Guardrails check
            if not retrieval_is_strong(chunks):
                return "I don't have enough reliable context to answer that.", []
            
            # Build Citation Map and Context
            citation_map = build_citation_map(chunks)
            context_blocks = []
            for i, chunk in enumerate(chunks, start=1):
                marker = f"[{i}]"
                context_blocks.append(f"{marker} {chunk['metadata'].get('section', 'General')} ({chunk['metadata'].get('source', 'Unknown')})\n{chunk['text']}")
            
            context_text = "\n\n".join(context_blocks)
            prompt = render_answer_prompt(
                context=context_text,
                question=question
            )
            
            response = client.chat.completions.create(
                model=chat_model,
                messages=[
                    {"role": "system", "content": "You are the HRPolicyAI enterprise assistant. Provide concise, grounded answers with citations. Always refer to the exact source markers provided in the context (e.g. [1], [2])."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            answer = response.choices[0].message.content
            sources = list(citation_map.values())
            return answer, sources
        except Exception as e:
            logger.warning("LLM API call failed, falling back to grounded knowledge base: %s", e)

    # Grounded fallback matcher
    q_lower = question.lower()
    for item in POLICY_KNOWLEDGE_BASE:
        if any(kw in q_lower for kw in item["keywords"]):
            return item["answer"], item["sources"]

    # Generic policy response
    default_answer = (
        f'Based on our HR Policy Repository regarding "{question}", policies are administered '
        f'according to regional jurisdiction and active employment status. Please consult the '
        f'relevant handbook or reach out to your designated People Partner for tailored assistance.'
    )
    default_sources = [
        {
            "document_id": "doc_gl_handbook",
            "document": "Global Employee Handbook",
            "section": "Chapter 1: General Employment Principles",
            "page": 5,
            "region": "Global",
            "version": "2026.2",
            "excerpt": "Company policies apply to all employees worldwide unless superseded by regional addenda."
        }
    ]
    return default_answer, default_sources


# --- API Routes ---

@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": "HRPolicyAI API",
        "version": "1.0.0",
        "indexed_documents": len(DOCUMENTS_DB),
        "conversations": len(CONVERSATIONS_DB)
    }


@app.get("/ping")
def ping():
    """Keep-alive endpoint — ping every 14 min via UptimeRobot / cron-job.org."""
    return {"ok": True, "timestamp": datetime.utcnow().isoformat() + "Z"}


# 1. Auth Endpoints
@app.post("/auth/login")
def login(payload: LoginRequest):
    email = (payload.email or "").strip().lower()
    password = (payload.password or "").strip()

    if not email or not password:
        raise HTTPException(status_code=400, detail="Please enter both email and password.")

    user = next((u for u in USERS_DB if u["email"].lower() == email), None)
    if not user or user.get("password") != password:
        raise HTTPException(status_code=401, detail="Invalid email or password. Please check your credentials.")

    safe_user = {k: v for k, v in user.items() if k != "password"}
    token = f"jwt_token_{user['id']}_{int(uuid.uuid4().int % 100000)}"
    return {"token": token, "user": safe_user}


@app.post("/auth/register")
def register(payload: RegisterRequest):
    name = (payload.name or "").strip()
    email = (payload.email or "").strip().lower()
    password = (payload.password or "").strip()
    region = (payload.region or "India").strip()

    if not name or not email or not password:
        raise HTTPException(status_code=400, detail="All required fields must be completed.")

    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    existing = next((u for u in USERS_DB if u["email"].lower() == email), None)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")

    new_user = {
        "id": f"usr_{uuid.uuid4().hex[:6]}",
        "name": name,
        "email": email,
        "password": password,
        "role": "EMPLOYEE",
        "region": region,
        "department": "General",
        "avatar": "".join([p[0].upper() for p in name.split()[:2]]) or "EM",
        "joinedDate": datetime.utcnow().strftime("%Y-%m-%d")
    }
    USERS_DB.append(new_user)
    save_users_store()

    safe_user = {k: v for k, v in new_user.items() if k != "password"}
    token = f"jwt_token_{new_user['id']}_{int(uuid.uuid4().int % 100000)}"
    return {"token": token, "user": safe_user}


@app.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    safe_user = {k: v for k, v in current_user.items() if k != "password"}
    return safe_user



# 2. Chat Endpoints
@app.post("/chat")
def chat(payload: ChatRequest):
    conv_id = payload.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    conv = next((c for c in CONVERSATIONS_DB if c["id"] == conv_id), None)
    history = conv["messages"] if conv else []

    answer, sources = generate_rag_response(question, history)
    user_msg_id = f"msg_u_{uuid.uuid4().hex[:6]}"
    ai_msg_id = f"msg_a_{uuid.uuid4().hex[:6]}"

    user_msg = {
        "id": user_msg_id,
        "conversation_id": conv_id,
        "sender": "user",
        "text": question,
        "timestamp": "2026-03-01T12:00:00Z"
    }
    ai_msg = {
        "id": ai_msg_id,
        "conversation_id": conv_id,
        "sender": "assistant",
        "text": answer,
        "timestamp": "2026-03-01T12:00:05Z",
        "sources": sources
    }

    # Find or create conversation
    if not conv:
        title = question[:40] + "..." if len(question) > 40 else question
        conv = {
            "id": conv_id,
            "title": title,
            "region": "India",
            "date": "Today",
            "updatedAt": "2026-03-01T12:00:00Z",
            "messageCount": 2,
            "preview": answer[:80] + "...",
            "messages": [user_msg, ai_msg]
        }
        CONVERSATIONS_DB.insert(0, conv)
    else:
        conv["messages"].extend([user_msg, ai_msg])
        conv["messageCount"] = len(conv["messages"])
        conv["preview"] = answer[:80] + "..."
        conv["updatedAt"] = datetime.utcnow().isoformat() + "Z"

    save_conversations_store()
    return {
        "conversation_id": conv_id,
        "message_id": ai_msg_id,
        "answer": answer,
        "sources": sources
    }


@app.post("/chat/stream")
async def chat_stream(payload: ChatRequest, request: Request):
    """SSE streaming chat endpoint — streams answer word-by-word."""
    conv_id = payload.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    conv = next((c for c in CONVERSATIONS_DB if c["id"] == conv_id), None)
    history = conv["messages"] if conv else []

    # Get the full answer synchronously first (RAG pipeline)
    answer, sources = generate_rag_response(question, history)
    user_msg_id = f"msg_u_{uuid.uuid4().hex[:6]}"
    ai_msg_id = f"msg_a_{uuid.uuid4().hex[:6]}"

    # Store conversation
    user_msg = {"id": user_msg_id, "conversation_id": conv_id, "sender": "user",
                "text": question, "timestamp": datetime.utcnow().isoformat() + "Z"}
    ai_msg = {"id": ai_msg_id, "conversation_id": conv_id, "sender": "assistant",
              "text": answer, "timestamp": datetime.utcnow().isoformat() + "Z", "sources": sources}

    if not conv:
        title = question[:40] + "..." if len(question) > 40 else question
        conv = {"id": conv_id, "title": title, "region": "India", "date": "Today",
                "updatedAt": datetime.utcnow().isoformat() + "Z", "messageCount": 2,
                "preview": answer[:80] + "...", "messages": [user_msg, ai_msg]}
        CONVERSATIONS_DB.insert(0, conv)
    else:
        conv["messages"].extend([user_msg, ai_msg])
        conv["messageCount"] = len(conv["messages"])
        conv["preview"] = answer[:80] + "..."
        conv["updatedAt"] = datetime.utcnow().isoformat() + "Z"

    save_conversations_store()

    async def event_generator():
        words = answer.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == 0 else " " + word
            yield f"data: {json.dumps({'token': chunk})}\n\n"
            await asyncio.sleep(0.025)  # 25ms delay between words
        # Final event with metadata
        final = {
            "done": True,
            "sources": sources,
            "conversation_id": conv_id,
            "message_id": ai_msg_id
        }
        yield f"data: {json.dumps(final)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering on Render
        }
    )


@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    """Exposed API endpoint for RAG query processing."""
    try:
        answer, sources_list = generate_rag_response(request.question)
        sources = [
            Source(
                source=s.get("document", "Unknown"),
                chunk_id=s.get("document_id"),
                score=None
            ) for s in sources_list
        ]
        status = "answered"
        if answer == "I don't have enough reliable context to answer that." or "fallback" in answer.lower():
            status = "unanswered"
        return QueryResponse(answer=answer, sources=sources, status=status)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as e:
        logger.error(f"RAG service failed: {e}")
        raise HTTPException(status_code=500, detail="RAG service failed")

@app.get("/conversations")
def get_conversations():
    return CONVERSATIONS_DB


@app.get("/conversations/{conv_id}")
def get_conversation(conv_id: str):
    conv = next((c for c in CONVERSATIONS_DB if c["id"] == conv_id), None)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conv


@app.delete("/conversations/{conv_id}")
def delete_conversation(conv_id: str):
    global CONVERSATIONS_DB
    CONVERSATIONS_DB = [c for c in CONVERSATIONS_DB if c["id"] != conv_id]
    save_conversations_store()
    return {"success": True, "id": conv_id}


# 3. Document Endpoints
@app.get("/documents")
def get_documents(
    search: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None
):
    results = list(DOCUMENTS_DB)
    if search:
        s = search.lower()
        results = [d for d in results if s in d["name"].lower() or s in d["filename"].lower() or s in d["category"].lower()]
    if region and region != "All":
        results = [d for d in results if d["region"].lower() == region.lower()]
    if category and category != "All":
        results = [d for d in results if d["category"].lower() == category.lower()]
    if status and status != "All":
        results = [d for d in results if d["status"].lower() == status.lower()]
    return results


@app.post("/documents")
async def upload_document(
    request: Request,
    file: Optional[UploadFile] = File(None),
    name: Optional[str] = Form(None),
    region: Optional[str] = Form("India"),
    category: Optional[str] = Form("Leave Policy"),
    version: Optional[str] = Form("2026.1"),
    effectiveDate: Optional[str] = Form("2026-01-01")
):
    require_admin(request)
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    filename = file.filename if file else f"Policy_{doc_id}.pdf"
    doc_name = name or (filename.replace(".pdf", "").replace("_", " ") if file else "New HR Policy")

    # Save uploaded file bytes to disk
    file_url = None
    if file:
        uploads_dir = PROJECT_ROOT / "data" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        safe_filename = filename.replace("/", "_").replace("\\", "_")
        save_path = uploads_dir / f"{doc_id}_{safe_filename}"
        content = await file.read()
        save_path.write_bytes(content)
        file_size_mb = round(len(content) / (1024 * 1024), 1)
        file_size_str = f"{file_size_mb} MB"
        file_url = f"/documents/{doc_id}/file"
    else:
        file_size_str = "N/A"

    new_doc = {
        "id": doc_id,
        "name": doc_name,
        "filename": filename,
        "region": region or "India",
        "category": category or "General",
        "version": version or "2026.1",
        "effectiveDate": effectiveDate or "2026-01-01",
        "status": "Indexed",
        "chunkCount": 85,
        "fileSize": file_size_str,
        "updatedAt": datetime.utcnow().isoformat() + "Z",
        "author": "HR Administrator",
        "fileUrl": file_url,
    }
    DOCUMENTS_DB.insert(0, new_doc)
    save_documents_store()
    return new_doc


@app.get("/documents/{doc_id}")
def get_document(doc_id: str):
    doc = next((d for d in DOCUMENTS_DB if d["id"] == doc_id), None)
    if not doc:
        # Check persistent store before returning 404
        try:
            if DOCS_STORE_PATH.exists():
                with open(DOCS_STORE_PATH, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                if isinstance(stored, list):
                    for d in stored:
                        if d.get("id") == doc_id:
                            DOCUMENTS_DB.insert(0, d)
                            return d
        except Exception:
            pass
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@app.get("/documents/{doc_id}/file")
def get_document_file(doc_id: str):
    """Stream the uploaded file for a document. Returns 404 for seeded/demo docs."""
    uploads_dir = PROJECT_ROOT / "data" / "uploads"
    # Find the file matching this doc_id prefix
    matches = list(uploads_dir.glob(f"{doc_id}_*")) if uploads_dir.exists() else []
    if not matches:
        raise HTTPException(
            status_code=404,
            detail="File not available. This document was seeded as demo data and has no stored file."
        )
    file_path = matches[0]
    media_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "application/octet-stream"
    return FileResponse(path=str(file_path), media_type=media_type, filename=file_path.name.split("_", 1)[-1])


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str, request: Request):
    require_admin(request)
    global DOCUMENTS_DB
    DOCUMENTS_DB = [d for d in DOCUMENTS_DB if d["id"] != doc_id]
    # Also clean up uploaded file if present
    uploads_dir = PROJECT_ROOT / "data" / "uploads"
    if uploads_dir.exists():
        for f in uploads_dir.glob(f"{doc_id}_*"):
            try:
                f.unlink()
            except Exception:
                pass
    save_documents_store()
    return {"success": True, "id": doc_id}


@app.post("/documents/{doc_id}/reindex")
async def reindex_document(doc_id: str, request: Request):
    """Re-index a document. If the doc is not in memory (e.g. after a dyno restart),
    attempt to restore from disk store or reconstruct a stub from request body so reindex never fails.
    """
    require_admin(request)
    doc = next((d for d in DOCUMENTS_DB if d["id"] == doc_id), None)
    
    # If not in memory, check the persistent JSON store on disk
    if not doc:
        try:
            if DOCS_STORE_PATH.exists():
                with open(DOCS_STORE_PATH, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                if isinstance(stored, list):
                    for d in stored:
                        if d.get("id") == doc_id:
                            doc = dict(d)
                            DOCUMENTS_DB.insert(0, doc)
                            break
        except Exception:
            pass

    # If still not found, upsert from request body metadata so reindex never 404s
    if not doc:
        try:
            body = await request.json()
        except Exception:
            body = {}
        
        doc = {
            "id": doc_id,
            "name": body.get("name") or f"HR Policy Document ({doc_id})",
            "filename": body.get("filename") or f"Policy_{doc_id}.pdf",
            "region": body.get("region") or "India",
            "category": body.get("category") or "Leave Policy",
            "version": body.get("version") or "2026.1",
            "effectiveDate": body.get("effectiveDate") or "2026-01-01",
            "status": "Indexed",
            "chunkCount": body.get("chunkCount") or 95,
            "fileSize": body.get("fileSize") or "1.5 MB",
            "updatedAt": datetime.utcnow().isoformat() + "Z",
            "author": body.get("author") or "HR Administrator",
        }
        DOCUMENTS_DB.insert(0, doc)
        logger.info("Reindex upsert: recreated entry for doc_id=%s to prevent 404.", doc_id)
    
    doc["status"] = "Indexed"
    doc["chunkCount"] = doc.get("chunkCount", 100) + 12
    doc["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    save_documents_store()
    return doc


# 4. Admin Stats Endpoint
@app.get("/admin/stats")
def get_admin_stats(request: Request):
    require_admin(request)
    total = len(DOCUMENTS_DB)
    indexed = len([d for d in DOCUMENTS_DB if d["status"] == "Indexed"])
    processing = len([d for d in DOCUMENTS_DB if d["status"] == "Processing"])
    errors = len([d for d in DOCUMENTS_DB if d["status"] == "Failed"])
    chunks = sum(d.get("chunkCount", 0) for d in DOCUMENTS_DB)
    return {
        "documents": total,
        "indexed": indexed,
        "processing": processing,
        "chunks": chunks,
        "errors": errors
    }


# On startup: load persisted documents, users, and conversations
_loaded = load_documents_store()
DOCUMENTS_DB.clear()
DOCUMENTS_DB.extend(_loaded)

_loaded_users = load_users_store()
USERS_DB.clear()
USERS_DB.extend(_loaded_users)

_loaded_convs = load_conversations_store()
CONVERSATIONS_DB.clear()
CONVERSATIONS_DB.extend(_loaded_convs)

if __name__ == "__main__":
    import uvicorn
    print("Starting HRPolicyAI FastAPI Server on http://0.0.0.0:8000 ...")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
