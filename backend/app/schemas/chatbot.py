from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class ChatbotCreate(BaseModel):
    name: str
    description: Optional[str] = None
    config: dict = {}


class ChatbotResponse(ChatbotCreate):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageRequest(BaseModel):
    content: str
    session_id: Optional[str] = None


class MessageResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID
    role: str
    content: str
    nlp_result: dict
    created_at: datetime


class ConversationResponse(BaseModel):
    id: UUID
    chatbot_id: UUID
    status: str
    messages: list[dict] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class NLPAnalyzeRequest(BaseModel):
    text: str


class NLPAnalyzeResponse(BaseModel):
    intent: str
    confidence: float
    entities: dict
    sentiment: str
    suggested_action: Optional[str]
