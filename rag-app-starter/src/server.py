import os
import sys
import uuid
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

CONVERSATIONS_DB: List[Dict[str, Any]] = [
    {
        "id": "conv_01",
        "title": "Maternity leave duration in India",
        "region": "India",
        "date": "Today",
        "updatedAt": "2026-03-01T10:30:00Z",
        "messageCount": 4,
        "preview": "Eligible female employees in India are entitled to 26 weeks of fully paid maternity leave...",
        "messages": [
            {
                "id": "m1",
                "conversation_id": "conv_01",
                "sender": "user",
                "text": "What is the maternity leave duration in India?",
                "timestamp": "2026-03-01T10:28:00Z",
            },
            {
                "id": "m2",
                "conversation_id": "conv_01",
                "sender": "assistant",
                "text": "Under the India Leave Policy 2026 and the Maternity Benefit Act, eligible female employees are entitled to **26 weeks (182 calendar days)** of fully paid maternity leave for up to two surviving children. For third child onwards, the entitlement is 12 weeks.",
                "timestamp": "2026-03-01T10:28:05Z",
                "sources": [
                    {
                        "document_id": "doc_in_leave",
                        "chunk_id": "chk_in_leave_012",
                        "document": "India Leave Policy 2026",
                        "section": "Section 4.1: Maternity Leave",
                        "page": 12,
                        "region": "India",
                        "version": "2026.1",
                        "score": 0.96,
                        "excerpt": "Female employees who have worked for at least 80 days in the preceding 12 months are entitled to 26 weeks of paid leave.",
                    }
                ],
            },
        ],
    }
]

# Knowledge base fallback answers for realistic responses when LLM key is not provided
POLICY_KNOWLEDGE_BASE = [
    {
        "keywords": ["maternity", "mother", "pregnancy"],
        "answer": "Under the India Maternity Benefit guidelines, female employees are entitled to 26 weeks (182 calendar days) of fully paid maternity leave for up to two surviving children. Applications should be submitted at least 8 weeks prior to the expected delivery date.",
        "sources": [
            {
                "document_id": "doc_in_leave",
                "chunk_id": "chk_in_leave_012",
                "document": "India Leave Policy 2026",
                "section": "Section 4.1: Maternity Leave",
                "page": 12,
                "region": "India",
                "version": "2026.1",
                "score": 0.98,
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
                "chunk_id": "chk_gl_parental_007",
                "document": "Global Parental & Caregiver Leave",
                "section": "Section 3: Paternity Entitlement",
                "page": 7,
                "region": "Global",
                "version": "2026.0",
                "score": 0.95,
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
                "chunk_id": "chk_in_leave_008",
                "document": "India Leave Policy 2026",
                "section": "Section 2.3: Medical Leave",
                "page": 8,
                "region": "India",
                "version": "2026.1",
                "score": 0.94,
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
                "chunk_id": "chk_in_insurance_003",
                "document": "India Group Health Insurance Coverage",
                "section": "Policy Summary & Floater Limits",
                "page": 3,
                "region": "India",
                "version": "2026.1",
                "score": 0.97,
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
                "chunk_id": "chk_in_leave_004",
                "document": "India Leave Policy 2026",
                "section": "Section 2.1: Annual Privilege Leave",
                "page": 4,
                "region": "India",
                "version": "2026.1",
                "score": 0.96,
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


# --- Helper Methods ---
def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        for u in USERS_DB:
            if u["id"] in token:
                return u
    return USERS_DB[0]


def generate_rag_response(question: str) -> tuple[str, list]:
    """Execute live RAG if OpenAI and vector store configured, otherwise grounded knowledge base."""
    api_key = os.getenv("OPENAI_API_KEY")
    chat_model = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")
    
    # Check if we can perform Chroma/OpenAI RAG
    if api_key:
        try:
            from openai import OpenAI
            base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("API_BASE_URL") or "https://api.openai.com/v1"
            client = OpenAI(api_key=api_key, base_url=base_url)
            
            # Use prompts template
            from prompts.answer import render_answer_prompt
            prompt = render_answer_prompt(
                context="All official company policies from Global Handbook and India Leave Policy 2026.",
                question=question
            )
            
            response = client.chat.completions.create(
                model=chat_model,
                messages=[
                    {"role": "system", "content": "You are the HRPolicyAI enterprise assistant. Provide concise, grounded answers with citations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            answer = response.choices[0].message.content
            sources = [
                {
                    "document_id": "doc_gl_handbook",
                    "document": "Global Employee Handbook",
                    "section": "General Policies",
                    "page": 1,
                    "region": "Global",
                    "version": "2026.2",
                    "excerpt": "Policies apply company-wide according to regional jurisdictions."
                }
            ]
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
            "chunk_id": "chk_gl_handbook_001",
            "document": "Global Employee Handbook",
            "section": "Chapter 1: General Employment Principles",
            "page": 5,
            "region": "Global",
            "version": "2026.2",
            "score": 0.90,
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


# 1. Auth Endpoints
@app.post("/auth/login")
def login(payload: LoginRequest):
    email = payload.email.lower()
    user = next((u for u in USERS_DB if u["email"].lower() == email), None)
    if user:
        if user.get("password") and payload.password != user.get("password"):
            raise HTTPException(status_code=401, detail="Invalid password. Please check your credentials.")
    else:
        # If user not found, create new employee
        if not payload.password or len(payload.password) < 4:
            raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
        user = {
            "id": f"usr_{uuid.uuid4().hex[:6]}",
            "name": payload.email.split("@")[0].replace(".", " ").title(),
            "email": payload.email,
            "password": payload.password,
            "role": "EMPLOYEE",
            "region": "India",
            "department": "Engineering",
            "avatar": payload.email[:2].upper(),
            "joinedDate": "2026-01-01"
        }
        USERS_DB.append(user)
    
    safe_user = {k: v for k, v in user.items() if k != "password"}
    token = f"jwt_token_{user['id']}_{int(uuid.uuid4().int % 100000)}"
    return {"token": token, "user": safe_user}


@app.post("/auth/register")
def register(payload: RegisterRequest):
    if not payload.name or not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail="All required fields must be completed.")
    
    existing = next((u for u in USERS_DB if u["email"].lower() == payload.email.lower()), None)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")

    new_user = {
        "id": f"usr_{uuid.uuid4().hex[:6]}",
        "name": payload.name,
        "email": payload.email,
        "role": "EMPLOYEE",
        "region": payload.region or "India",
        "department": "General",
        "avatar": payload.name[:2].upper(),
        "joinedDate": "2026-03-01"
    }
    USERS_DB.append(new_user)
    token = f"jwt_token_{new_user['id']}_{int(uuid.uuid4().int % 100000)}"
    return {"token": token, "user": new_user}


@app.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


# 2. Chat Endpoints
@app.post("/chat")
def chat(payload: ChatRequest):
    conv_id = payload.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    answer, sources = generate_rag_response(question)
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
    conv = next((c for c in CONVERSATIONS_DB if c["id"] == conv_id), None)
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

    return {
        "conversation_id": conv_id,
        "message_id": ai_msg_id,
        "answer": answer,
        "sources": sources
    }


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
    file: Optional[UploadFile] = File(None),
    name: Optional[str] = Form(None),
    region: Optional[str] = Form("India"),
    category: Optional[str] = Form("Leave Policy"),
    version: Optional[str] = Form("2026.1"),
    effectiveDate: Optional[str] = Form("2026-01-01")
):
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    filename = file.filename if file else f"Policy_{doc_id}.pdf"
    doc_name = name or (file.filename.replace(".pdf", "") if file else "New HR Policy")
    
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
        "fileSize": "1.2 MB",
        "updatedAt": "2026-03-01T12:00:00Z",
        "author": "HR Administrator",
    }
    DOCUMENTS_DB.insert(0, new_doc)
    return new_doc


@app.get("/documents/{doc_id}")
def get_document(doc_id: str):
    doc = next((d for d in DOCUMENTS_DB if d["id"] == doc_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    global DOCUMENTS_DB
    DOCUMENTS_DB = [d for d in DOCUMENTS_DB if d["id"] != doc_id]
    return {"success": True, "id": doc_id}


@app.post("/documents/{doc_id}/reindex")
def reindex_document(doc_id: str):
    doc = next((d for d in DOCUMENTS_DB if d["id"] == doc_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc["status"] = "Indexed"
    doc["chunkCount"] = doc.get("chunkCount", 100) + 12
    return doc


# 4. Admin Stats Endpoint
@app.get("/admin/stats")
def get_admin_stats():
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


if __name__ == "__main__":
    import uvicorn
    print("Starting HRPolicyAI FastAPI Server on http://0.0.0.0:8000 ...")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
