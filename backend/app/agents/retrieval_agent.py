"""
Retrieval Agent: Fetches relevant documents from ChromaDB with intelligent filtering.

This agent is responsible for:
1. Retrieving documents matching user's department
2. Including common documents accessible to all
3. Ranking and filtering results by relevance
4. Returning document metadata for transparency
"""
from starlette.config import Config
import chromadb
from typing import List, Dict, Any, Tuple

config = Config('.env')
CHROMA_HOST = config('CHROMA_HOST', cast=str, default='chromadb')
CHROMA_PORT = config('CHROMA_PORT', cast=str, default='8000')

# Initialize ChromaDB client
chroma = chromadb.HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))
collection = chroma.get_or_create_collection("documents")


def retrieve_documents(query_embedding: List[float], department: str, top_k: int = 5) -> List[str]:
    """
    Retrieve top_k documents from ChromaDB for a given embedding and department.
    Also retrieves common documents accessible to all departments.
    
    Args:
        query_embedding: Vector embedding of the user's question
        department: User's department for filtering
        top_k: Maximum number of documents to retrieve
        
    Returns:
        List of document texts (empty if none found)
    """
    try:
        # Query for department-specific documents AND common documents
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "$or": [
                    {"department": department},
                    {"category": "common"}
                ]
            }
        )
        print(f"[RetrievalAgent] Query for department '{department}' + common docs")
        
        docs = results.get('documents', [[]])
        if docs and isinstance(docs, list):
            retrieved = docs[0] if docs[0] else []
            print(f"[RetrievalAgent] Retrieved {len(retrieved)} documents")
            return retrieved
        return []
        
    except Exception as e:
        print(f"[RetrievalAgent] Error during retrieval: {e}")
        return []


def retrieve_documents_with_metadata(
    query_embedding: List[float], 
    department: str, 
    top_k: int = 5
) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
    """
    Retrieve documents with their metadata and relevance scores.
    
    Args:
        query_embedding: Vector embedding of the user's question
        department: User's department for filtering
        top_k: Maximum number of documents to retrieve
        
    Returns:
        Tuple of (documents, metadatas, distances)
    """
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "$or": [
                    {"department": department},
                    {"category": "common"}
                ]
            },
            include=["documents", "metadatas", "distances"]
        )
        
        docs = results.get('documents', [[]])[0] if results.get('documents') else []
        metadatas = results.get('metadatas', [[]])[0] if results.get('metadatas') else []
        distances = results.get('distances', [[]])[0] if results.get('distances') else []
        
        print(f"[RetrievalAgent] Retrieved {len(docs)} docs with metadata")
        for i, meta in enumerate(metadatas):
            print(f"  - {meta.get('name', 'Unknown')} (distance: {distances[i]:.4f})")
        
        return docs, metadatas, distances
        
    except Exception as e:
        print(f"[RetrievalAgent] Error: {e}")
        return [], [], []


def get_relevant_context(
    query_embedding: List[float],
    department: str,
    top_k: int = 5,
    max_context_length: int = 4000
) -> str:
    """
    Get concatenated context from relevant documents, with source attribution.
    Limits total context length to avoid exceeding LLM token limits.
    
    Args:
        query_embedding: Vector embedding of the user's question
        department: User's department for filtering
        top_k: Maximum number of documents to retrieve
        max_context_length: Maximum character length of combined context
        
    Returns:
        Formatted context string with source citations
    """
    docs, metadatas, distances = retrieve_documents_with_metadata(
        query_embedding, department, top_k
    )
    
    if not docs:
        return ""
    
    context_parts = []
    total_length = 0
    
    for i, (doc, meta) in enumerate(zip(docs, metadatas)):
        source = meta.get('name', f'Document {i+1}')
        dept = meta.get('department', 'Unknown')
        category = meta.get('category', 'department')
        
        # Add source header
        header = f"\n--- Source: {source} ({dept if category != 'common' else 'Common'}) ---\n"
        
        # Check if we have room for this document
        if total_length + len(header) + len(doc) > max_context_length:
            # Truncate document to fit
            remaining = max_context_length - total_length - len(header) - 50
            if remaining > 100:
                context_parts.append(header + doc[:remaining] + "... [truncated]")
            break
        
        context_parts.append(header + doc)
        total_length += len(header) + len(doc)
    
    return "\n".join(context_parts)
