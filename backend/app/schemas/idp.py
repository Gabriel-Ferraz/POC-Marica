from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class IDPDocumentResponse(BaseModel):
    id: UUID
    filename: str
    mime_type: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class IDPJobResponse(BaseModel):
    id: UUID
    document_id: UUID
    status: str
    celery_task_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class IDPResultResponse(BaseModel):
    id: UUID
    document_id: UUID
    document_type: Optional[str]
    confidence: float
    raw_text: Optional[str]
    has_handwriting: bool
    json_export: dict
    created_at: datetime

    model_config = {"from_attributes": True}
