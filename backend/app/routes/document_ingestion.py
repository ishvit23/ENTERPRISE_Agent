import os

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.auth.jwt_utils import get_current_user
from app.services.document_ingestion import ingest_document
from app.services import document_ingestion as doc_service

router = APIRouter()

@router.delete("/delete/{doc_id}")
def delete_document(doc_id: str, user=Depends(get_current_user)):
    # Only admin can delete
    is_admin = False
    if user:
        if user.get('role') == 'admin':
            is_admin = True
        elif isinstance(user.get('roles'), list) and 'admin' in user['roles']:
            is_admin = True
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required to delete documents.")
    try:
        doc_service.collection.delete(ids=[doc_id])
        with open("logs/feature_log.txt", "a") as logf:
            logf.write(f"DELETE | user={user.get('sub')} | role={user.get('role')} | doc_id={doc_id}\n")
        return {"status": "deleted", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    department: str = Form(...),
    name: str = Form(...),
    version: str = Form(...),
    category: str = Form("department"),
    user=Depends(get_current_user)
):
    # Check for admin role
    is_admin = False
    if user:
        if user.get('role') == 'admin':
            is_admin = True
        elif isinstance(user.get('roles'), list) and 'admin' in user['roles']:
            is_admin = True
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required to upload documents.")
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/feature_log.txt", "a") as logf:
            logf.write(f"[DEBUG] Starting file read for upload: name={name}, department={department}, version={version}\n")
        content = await file.read()
        with open("logs/feature_log.txt", "a") as logf:
            logf.write(f"[DEBUG] File read complete, {len(content)} bytes. Attempting decode...\n")
        try:
            text = content.decode("utf-8")
        except Exception as decode_err:
            with open("logs/feature_log.txt", "a") as logf:
                logf.write(f"[ERROR] File decode failed: {decode_err}\n")
            raise HTTPException(status_code=400, detail=f"File decode error: {decode_err}")
        with open("logs/feature_log.txt", "a") as logf:
            logf.write(f"[DEBUG] Decode successful. Calling ingest_document...\n")
        try:
            success = ingest_document(text, name, department, version, category)
        except Exception as ingest_err:
            import traceback
            with open("logs/feature_log.txt", "a") as logf:
                logf.write(f"[ERROR] ingest_document failed: {ingest_err}\n{traceback.format_exc()}\n")
            raise HTTPException(status_code=500, detail=f"Ingestion error: {ingest_err}")
        # Log upload action
        with open("logs/feature_log.txt", "a") as logf:
            logf.write(f"UPLOAD | user={user.get('sub')} | role={user.get('role')} | department={user.get('department')} | name={name} | version={version} | category={category}\n")
        if not success:
            with open("logs/feature_log.txt", "a") as logf:
                logf.write(f"[ERROR] ingest_document returned False\n")
            raise HTTPException(status_code=500, detail="Ingestion failed.")
        with open("logs/feature_log.txt", "a") as logf:
            logf.write(f"[DEBUG] Ingestion successful. Returning success.\n")
        return {"status": "success"}
    except Exception as e:
        import traceback
        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/feature_log.txt", "a") as logf:
                logf.write(f"[ERROR] Exception in /ingest: {e}\n{traceback.format_exc()}\n")
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
def list_documents(user=Depends(get_current_user)):
    try:
        all_docs = doc_service.collection.get()
        documents = []
        ids = all_docs.get('ids', [])
        metadatas = all_docs.get('metadatas', [])
        is_admin = False
        if user:
            if user.get('role') == 'admin':
                is_admin = True
            elif isinstance(user.get('roles'), list) and 'admin' in user['roles']:
                is_admin = True
        for i, meta in enumerate(metadatas):
            # Show documents if:
            # 1. User is admin (sees everything)
            # 2. Document's department matches user's department
            # 3. Document's category is 'common' (visible to all)
            is_common = meta.get('category') == 'common'
            is_user_dept = user and meta.get('department') == user.get('department')
            if is_admin or is_user_dept or is_common:
                doc = {"id": ids[i] if i < len(ids) else "", **meta}
                documents.append(doc)
        # Log document listing
        with open("logs/feature_log.txt", "a") as logf:
            logf.write(f"LIST | user={user.get('sub')} | role={user.get('role')} | department={user.get('department')} | returned={len(documents)}\n")
        return {"documents": documents}
    except Exception as e:
        return {"documents": [], "error": str(e)}

@router.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    department: str = Form(...),
    name: str = Form(...),
    version: str = Form(...)
):
    try:
        content = await file.read()
        text = content.decode("utf-8")
        success = ingest_document(text, name, department, version)
        if not success:
            raise HTTPException(status_code=500, detail="Ingestion failed.")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
