import hashlib
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.process import ProcessSignature
from app.services import dlt_service, process_service


def create_signature_request(db: Session, process_id: UUID, attachment_id: UUID, signer_ids: list[UUID]) -> ProcessSignature:
    sig = ProcessSignature(
        process_id=process_id,
        attachment_id=attachment_id,
        status="in_progress",
        signers=[{"user_id": str(uid), "signed_at": None, "signature_hash": None} for uid in signer_ids],
        required_signers_count=str(len(signer_ids)),
    )
    db.add(sig)
    db.flush()
    return sig


def sign_document(db: Session, signature_id: UUID, user_id: UUID, note: str | None = None) -> ProcessSignature:
    sig = db.query(ProcessSignature).filter(ProcessSignature.id == signature_id).first()
    if not sig:
        raise ValueError("Signature request not found")

    signers = list(sig.signers)
    signature_hash = hashlib.sha256(f"{user_id}:{signature_id}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()

    for s in signers:
        if s["user_id"] == str(user_id) and s["signed_at"] is None:
            s["signed_at"] = datetime.now(timezone.utc).isoformat()
            s["signature_hash"] = signature_hash
            break

    sig.signers = signers

    all_signed = all(s["signed_at"] is not None for s in signers)
    if all_signed:
        sig.status = "completed"
        sig.completed_at = datetime.now(timezone.utc)

        process = sig.process
        dlt_service.record_event(
            db=db,
            event_type="DOCUMENT_SIGNED",
            payload={"signature_id": str(signature_id), "signers": signers},
            workflow_id=process.workflow_id,
            process_id=process.id,
        )

        process_service.accept_process(db, process, user_id, comment="Auto-advanced after all signatures completed")

    db.commit()
    db.refresh(sig)
    return sig
