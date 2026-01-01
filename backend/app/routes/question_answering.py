"""
Question answering route: handles user queries using retrieval, answer, and escalation agents.

Enhanced with:
- Policy-based access control with audit logging
- Context-aware retrieval with source attribution
- Confidence scoring and escalation routing
- Sensitive content detection
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from app.agents.retrieval_agent import retrieve_documents, get_relevant_context, retrieve_documents_with_metadata
from app.agents.answer_agent import generate_answer
from app.agents.escalation_agent import should_escalate, get_escalation_details, format_escalation_message
from app.agents.policy_agent import check_policy, check_sensitive_content
from app.auth.jwt_utils import get_current_user
from starlette.config import Config
from sentence_transformers import SentenceTransformer
import os

class QARequest(BaseModel):
    question: str
    department: Optional[str] = None  # If not provided, use user's department
    top_k: int = 5

class QAResponse(BaseModel):
    answer: str
    confidence: float
    escalate: bool
    escalation_details: Optional[dict] = None
    sources: Optional[List[dict]] = None
    context: Optional[List[str]] = None

router = APIRouter()

# Initialize embedding model once
config = Config('.env')
EMBEDDING_MODEL = config('EMBEDDING_MODEL', cast=str, default='all-MiniLM-L6-v2')
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model

@router.post("/ask", response_model=QAResponse)
def ask_question(request: QARequest, user=Depends(get_current_user)):
    """
    Process a user's question using the RAG pipeline.
    
    1. Policy check - verify user has access
    2. Embed the question
    3. Retrieve relevant documents
    4. Generate answer with LLM
    5. Check if escalation is needed
    """
    # Use user's department if not specified
    department = request.department or user.get('department', 'HR')
    
    # Policy check (department match)
    allowed, reason = check_policy(user, {"department": department})
    if not allowed:
        raise HTTPException(status_code=403, detail=reason)

    # Check for sensitive content in question
    sensitive_findings = check_sensitive_content(request.question)
    if sensitive_findings:
        print(f"[QA] Warning: Question contains sensitive data patterns")

    # Embed the question
    model = get_embedding_model()
    query_embedding = model.encode(request.question).tolist()
    
    # Retrieve documents with metadata for source attribution
    docs, metadatas, distances = retrieve_documents_with_metadata(
        query_embedding, 
        department, 
        request.top_k
    )
    
    # Build context with source attribution
    context = get_relevant_context(query_embedding, department, request.top_k)
    
    # Generate answer with user's department context
    answer, confidence = generate_answer(
        request.question, 
        context, 
        user_department=department
    )
    
    # Get detailed escalation information
    escalation_details = get_escalation_details(
        answer, 
        confidence, 
        request.question, 
        user
    )
    escalate = escalation_details.get('should_escalate', False)
    
    # Format answer with escalation message if needed
    if escalate:
        answer = format_escalation_message(escalation_details, answer)
    
    # Build sources list for transparency
    sources = []
    for i, meta in enumerate(metadatas):
        sources.append({
            "name": meta.get('name', f'Document {i+1}'),
            "department": meta.get('department', 'Unknown'),
            "category": meta.get('category', 'department'),
            "relevance": 1.0 - (distances[i] if i < len(distances) else 0.5)
        })
    
    # Log Q&A action
    os.makedirs("logs", exist_ok=True)
    with open("logs/feature_log.txt", "a") as logf:
        logf.write(
            f"QNA | user={user.get('sub')} | role={user.get('role')} | "
            f"department={department} | question={request.question[:100]} | "
            f"confidence={confidence:.2f} | escalate={escalate} | "
            f"sources={len(sources)}\n"
        )
    
    return QAResponse(
        answer=answer,
        confidence=confidence,
        escalate=escalate,
        escalation_details=escalation_details if escalate else None,
        sources=sources,
        context=docs
    )
