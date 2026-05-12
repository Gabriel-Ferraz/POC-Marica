from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class VoiceBotCreate(BaseModel):
    name: str
    config: dict = {}


class VoiceBotResponse(VoiceBotCreate):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class VoiceCallResponse(BaseModel):
    id: UUID
    session_id: Optional[str]
    status: str
    transcripts: list[dict] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class VoiceCampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ideal_hours: list[int] = []


class VoiceCampaignResponse(VoiceCampaignCreate):
    id: UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
