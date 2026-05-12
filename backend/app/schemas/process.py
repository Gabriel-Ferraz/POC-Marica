from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class ProcessCreate(BaseModel):
    workflow_id: UUID
    title: str
    form_data: dict = {}


class ProcessResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    current_step_id: Optional[UUID]
    started_by: UUID
    title: str
    status: str
    form_data: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class ProcessActionRequest(BaseModel):
    comment: Optional[str] = None
    form_data: Optional[dict] = None


class ProcessActivityResponse(BaseModel):
    id: UUID
    process_id: UUID
    user_id: UUID
    action: str
    from_step_id: Optional[UUID]
    to_step_id: Optional[UUID]
    comment: Optional[str]
    dlt_hash: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class SignatureCreate(BaseModel):
    attachment_id: UUID
    signer_user_ids: list[UUID]


class SignerAction(BaseModel):
    user_id: UUID
    signature_note: Optional[str] = None
