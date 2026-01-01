"""
Document ingestion service: embeds and stores documents in ChromaDB with department info.
"""
from starlette.config import Config
import chromadb
from sentence_transformers import SentenceTransformer
import os

config = Config('.env')
CHROMA_HOST = config('CHROMA_HOST', cast=str, default='')
CHROMA_PORT = config('CHROMA_PORT', cast=str, default='8000')

# Initialize ChromaDB client - use PersistentClient for cloud, HttpClient for Docker
if CHROMA_HOST and CHROMA_HOST != '':
    # Docker/local development with separate ChromaDB server
    chroma = chromadb.HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))
else:
    # Cloud deployment (Render) - use persistent local storage
    persist_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'chroma_data')
    os.makedirs(persist_dir, exist_ok=True)
    chroma = chromadb.PersistentClient(path=persist_dir)

collection = chroma.get_or_create_collection("documents")

# Use a lightweight model for demo; replace with production model as needed
EMBEDDING_MODEL = config('EMBEDDING_MODEL', cast=str, default='all-MiniLM-L6-v2')
model = SentenceTransformer(EMBEDDING_MODEL)

def ingest_document(text, name, department, version, category="department"):
    try:
        embedding = model.encode(text).tolist()
        # Use name+version as unique ID
        doc_id = f"{name}:{version}"
        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[doc_id],
            metadatas=[{"department": department, "name": name, "version": version, "category": category}]
        )
        # Debug: print all documents in the collection after adding
        try:
            all_docs = collection.get()
            print("[DocumentIngestion] All documents in collection after ingest:")
            print(all_docs)
        except Exception as e:
            print(f"[DocumentIngestion] Error fetching all documents: {e}")
        return True
    except Exception as e:
        print(f"[DocumentIngestion] Error: {e}")
        return False
