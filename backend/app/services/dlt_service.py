import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.dlt import DLTRecord


def generate_record_hash(payload: dict) -> str:
    normalized = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def record_event(
    db: Session,
    event_type: str,
    payload: dict,
    network_id: UUID | None = None,
    contract_id: UUID | None = None,
    workflow_id: UUID | None = None,
    process_id: UUID | None = None,
) -> DLTRecord:
    full_payload = {
        "network_id": str(network_id) if network_id else None,
        "contract_id": str(contract_id) if contract_id else None,
        "workflow_id": str(workflow_id) if workflow_id else None,
        "process_id": str(process_id) if process_id else None,
        "event_type": event_type,
        "payload": payload,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    record_hash = generate_record_hash(full_payload)
    record = DLTRecord(
        network_id=network_id,
        contract_id=contract_id,
        workflow_id=workflow_id,
        process_id=process_id,
        event_type=event_type,
        payload=payload,
        record_hash=record_hash,
    )
    db.add(record)
    db.flush()
    return record
