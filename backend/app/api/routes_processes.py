import os
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.process import ProcessAttachment, ProcessInstance
from app.models.user import User
from app.schemas.process import (
    ProcessActionRequest, ProcessActivityResponse, ProcessCreate, ProcessResponse, SignatureCreate, SignerAction,
)
from app.services import process_service, signature_service

router = APIRouter(prefix="/api/processes", tags=["processes"])


@router.post("", response_model=ProcessResponse, status_code=201)
def create_process(payload: ProcessCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.workflow import Workflow, WorkflowStep
    wf = db.query(Workflow).filter(Workflow.id == payload.workflow_id).first()
    if not wf:
        raise HTTPException(404, "Workflow not found")
    first_step = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == wf.id).order_by(WorkflowStep.order).first()
    proc = ProcessInstance(
        workflow_id=payload.workflow_id,
        title=payload.title,
        form_data=payload.form_data,
        started_by=current_user.id,
        current_step_id=first_step.id if first_step else None,
    )
    db.add(proc)
    db.commit()
    db.refresh(proc)
    return proc


@router.get("/{process_id}", response_model=ProcessResponse)
def get_process(process_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    proc = db.query(ProcessInstance).filter(ProcessInstance.id == process_id).first()
    if not proc:
        raise HTTPException(404, "Process not found")
    return proc


@router.post("/{process_id}/accept", response_model=ProcessResponse)
def accept(process_id: UUID, payload: ProcessActionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proc = db.query(ProcessInstance).filter(ProcessInstance.id == process_id).first()
    if not proc:
        raise HTTPException(404, "Process not found")
    return process_service.accept_process(db, proc, current_user.id, payload.comment)


@router.post("/{process_id}/return", response_model=ProcessResponse)
def return_process(process_id: UUID, payload: ProcessActionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proc = db.query(ProcessInstance).filter(ProcessInstance.id == process_id).first()
    if not proc:
        raise HTTPException(404, "Process not found")
    return process_service.return_process(db, proc, current_user.id, payload.comment)


@router.get("/{process_id}/history", response_model=List[ProcessActivityResponse])
def history(process_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    proc = db.query(ProcessInstance).filter(ProcessInstance.id == process_id).first()
    if not proc:
        raise HTTPException(404, "Process not found")
    return proc.activities


@router.get("/{process_id}/documents")
def list_documents(process_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    attachments = db.query(ProcessAttachment).filter(ProcessAttachment.process_id == process_id).all()
    return [
        {
            "id": str(a.id),
            "filename": a.filename,
            "mime_type": a.mime_type,
            "is_signature_attachment": a.is_signature_attachment,
            "created_at": a.created_at.isoformat(),
        }
        for a in attachments
    ]


@router.post("/{process_id}/upload")
async def upload_attachment(
    process_id: UUID,
    file: UploadFile = File(...),
    is_signature: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proc = db.query(ProcessInstance).filter(ProcessInstance.id == process_id).first()
    if not proc:
        raise HTTPException(404, "Process not found")

    upload_dir = os.path.join(settings.UPLOAD_DIR, str(process_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    attachment = ProcessAttachment(
        process_id=process_id,
        filename=file.filename,
        file_path=file_path,
        mime_type=file.content_type,
        is_signature_attachment=is_signature,
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return {"id": str(attachment.id), "filename": attachment.filename}


# Signatures
@router.post("/{process_id}/signatures", status_code=201)
def create_signature(process_id: UUID, payload: SignatureCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    sig = signature_service.create_signature_request(db, process_id, payload.attachment_id, payload.signer_user_ids)
    return {"id": str(sig.id), "status": sig.status}


@router.post("/{process_id}/signatures/{signature_id}/sign")
def sign(process_id: UUID, signature_id: UUID, payload: SignerAction, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    sig = signature_service.sign_document(db, signature_id, payload.user_id, payload.signature_note)
    return {"id": str(sig.id), "status": sig.status}
