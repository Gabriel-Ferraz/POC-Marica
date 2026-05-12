import os
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.idp import IDPDocument, IDPExtractedField, IDPProcessingJob, IDPResult
from app.models.user import User
from app.schemas.idp import IDPDocumentResponse, IDPJobResponse, IDPResultResponse
from app.services import idp_service

router = APIRouter(prefix="/api/idp", tags=["idp"])


@router.get("/documents", response_model=List[IDPDocumentResponse])
def list_documents(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(IDPDocument).all()


@router.post("/documents", response_model=IDPDocumentResponse, status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    upload_dir = os.path.join(settings.UPLOAD_DIR, "idp")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    doc = IDPDocument(
        filename=file.filename,
        file_path=file_path,
        mime_type=file.content_type,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.post("/documents/{document_id}/process", response_model=IDPJobResponse)
def process_document(document_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    doc = db.query(IDPDocument).filter(IDPDocument.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    job = IDPProcessingJob(document_id=document_id, status="processing")
    db.add(job)
    db.flush()

    try:
        with open(doc.file_path, "rb") as f:
            file_bytes = f.read()
        result_data = idp_service.process_document(file_bytes, doc.mime_type or "image/png")

        existing = db.query(IDPResult).filter(IDPResult.document_id == document_id).first()
        if existing:
            db.delete(existing)
            db.flush()

        result = IDPResult(
            document_id=document_id,
            document_type=result_data["document_type"],
            confidence=result_data["confidence"],
            raw_text=result_data["raw_text"],
            has_handwriting=result_data.get("has_handwriting", False),
            json_export=result_data["json_export"],
        )
        db.add(result)
        db.flush()

        for field_name, field_value in result_data.get("fields", {}).items():
            db.add(IDPExtractedField(result_id=result.id, field_name=field_name, field_value=str(field_value), confidence=result_data["confidence"]))

        job.status = "completed"
    except Exception as e:
        job.status = "failed"
        job.error = str(e)

    db.commit()
    db.refresh(job)
    return job


@router.get("/documents/{document_id}/result", response_model=IDPResultResponse)
def get_result(document_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    result = db.query(IDPResult).filter(IDPResult.document_id == document_id).first()
    if not result:
        raise HTTPException(404, "Result not found — process the document first")
    return result


@router.get("/documents/{document_id}/json")
def get_json(document_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    result = db.query(IDPResult).filter(IDPResult.document_id == document_id).first()
    if not result:
        raise HTTPException(404, "Result not found")
    return result.json_export
