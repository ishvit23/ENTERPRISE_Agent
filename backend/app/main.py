from fastapi import WebSocket, WebSocketDisconnect
from app.agents.retrieval_agent import retrieve_documents, get_relevant_context, retrieve_documents_with_metadata
from app.agents.answer_agent import generate_answer
from app.agents.escalation_agent import should_escalate, get_escalation_details, format_escalation_message
from app.agents.policy_agent import check_policy
from starlette.config import Config
from sentence_transformers import SentenceTransformer
import os

# Entry point for FastAPI backend

from fastapi import FastAPI, Request, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.auth import google_oauth
from app.auth.jwt_utils import get_current_user


from app.routes import document_ingestion
from app.routes import question_answering
from app.routes import register
from app.routes import admin_users
from app.routes import password_reset

# Initialize embedding model once (singleton pattern)
config = Config('.env')
EMBEDDING_MODEL = config('EMBEDDING_MODEL', cast=str, default='all-MiniLM-L6-v2')
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


app = FastAPI()

# WebSocket endpoint for real-time answer streaming (must be after app is defined)
@app.websocket("/ws/qa")
async def websocket_qa(websocket: WebSocket):
    """
    WebSocket endpoint for real-time Q&A with streaming support.
    
    Expected message format:
    {
        "question": "User's question",
        "department": "HR",
        "top_k": 5,
        "user": { "sub": "email", "department": "HR", "role": "user" }
    }
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            question = data.get("question")
            department = data.get("department")
            top_k = data.get("top_k", 5)
            user = data.get("user")  # In production, validate JWT here
            
            # Policy check (department match)
            allowed, reason = check_policy(user, {"department": department})
            if not allowed:
                await websocket.send_json({"error": reason})
                continue
            
            # Embed the question
            model = get_embedding_model()
            query_embedding = model.encode(question).tolist()
            
            # Retrieve documents with metadata
            docs, metadatas, distances = retrieve_documents_with_metadata(
                query_embedding, 
                department, 
                top_k
            )
            
            # Get formatted context with source attribution
            context = get_relevant_context(query_embedding, department, top_k)
            
            # Generate answer with department context
            answer, confidence = generate_answer(
                question, 
                context, 
                user_department=department
            )
            
            # Get detailed escalation information
            escalation_details = get_escalation_details(
                answer, 
                confidence, 
                question, 
                user
            )
            escalate = escalation_details.get('should_escalate', False)
            
            # Format answer with escalation message if needed
            if escalate:
                answer = format_escalation_message(escalation_details, answer)
            
            # Build sources list
            sources = []
            for i, meta in enumerate(metadatas):
                sources.append({
                    "name": meta.get('name', f'Document {i+1}'),
                    "department": meta.get('department', 'Unknown'),
                    "category": meta.get('category', 'department'),
                    "relevance": round(1.0 - (distances[i] if i < len(distances) else 0.5), 3)
                })
            
            # Send response
            await websocket.send_json({
                "answer": answer,
                "confidence": round(confidence, 3),
                "escalate": escalate,
                "escalation_details": escalation_details if escalate else None,
                "sources": sources,
                "context": docs
            })
            
            # Log the interaction
            os.makedirs("logs", exist_ok=True)
            with open("logs/feature_log.txt", "a") as logf:
                logf.write(
                    f"WS_QNA | user={user.get('sub') if user else 'unknown'} | "
                    f"department={department} | question={question[:100]} | "
                    f"confidence={confidence:.2f} | escalate={escalate}\n"
                )
                
    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected")

# Add JWT Bearer security scheme to OpenAPI docs
def custom_openapi():
	if app.openapi_schema:
		return app.openapi_schema
	openapi_schema = get_openapi(
		title=app.title,
		version=app.version,
		description=app.description,
		routes=app.routes,
	)
	openapi_schema["components"]["securitySchemes"] = {
		"BearerAuth": {
			"type": "http",
			"scheme": "bearer",
			"bearerFormat": "JWT"
		}
	}
	for path in openapi_schema["paths"].values():
		for op in path.values():
			op["security"] = [{"BearerAuth": []}]
	app.openapi_schema = openapi_schema
	return app.openapi_schema
app.openapi = custom_openapi

# Enable CORS for frontend
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
)


# Include authentication routes
app.include_router(google_oauth.router)

# Include document ingestion route
app.include_router(document_ingestion.router, prefix="/documents", tags=["documents"])
# Include question answering route

app.include_router(question_answering.router, prefix="/qa", tags=["qa"])
# Include register route
app.include_router(register.router, prefix="/auth", tags=["auth"])
app.include_router(admin_users.router, tags=["admin"])
app.include_router(password_reset.router, tags=["auth"])


# User profile endpoint
@app.get('/profile')
def get_profile(user=Depends(get_current_user)):
	return {
		"email": user.get("sub"),
		"name": user.get("name", ""),
		"department": user.get("department", ""),
		"role": user.get("role", ""),
		"roles": user.get("roles", [])
	}
