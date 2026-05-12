from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.chatbot import Chatbot, Conversation, ConversationMessage, ConversationSummary
from app.models.user import User
from app.schemas.chatbot import (
    ChatbotCreate, ChatbotResponse, ConversationResponse,
    MessageRequest, MessageResponse, NLPAnalyzeRequest, NLPAnalyzeResponse,
)
from app.services import nlp_service

router = APIRouter(prefix="/api/chatbots", tags=["chatbots"])


@router.get("", response_model=List[ChatbotResponse])
def list_chatbots(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Chatbot).all()


@router.post("", response_model=ChatbotResponse, status_code=201)
def create_chatbot(payload: ChatbotCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    bot = Chatbot(**payload.model_dump())
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot


@router.post("/{chatbot_id}/message")
async def send_message(chatbot_id: UUID, payload: MessageRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not bot:
        raise HTTPException(404, "Chatbot not found")

    conv = None
    if payload.session_id:
        conv = db.query(Conversation).filter(
            Conversation.chatbot_id == chatbot_id,
            Conversation.session_id == payload.session_id,
        ).first()

    if not conv:
        import uuid
        conv = Conversation(
            chatbot_id=chatbot_id,
            user_id=current_user.id,
            session_id=payload.session_id or str(uuid.uuid4()),
        )
        db.add(conv)
        db.flush()

    nlp_result = await nlp_service.analyze(payload.content)

    user_msg = ConversationMessage(
        conversation_id=conv.id,
        role="user",
        content=payload.content,
        nlp_result=nlp_result,
    )
    db.add(user_msg)

    bot_msg = ConversationMessage(
        conversation_id=conv.id,
        role="assistant",
        content=nlp_result.get("response", "Como posso ajudá-lo?"),
        nlp_result={},
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)

    return {
        "conversation_id": str(conv.id),
        "message_id": str(bot_msg.id),
        "role": "assistant",
        "content": bot_msg.content,
        "nlp_result": nlp_result,
        "created_at": bot_msg.created_at.isoformat(),
    }


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return {
        "id": str(conv.id),
        "chatbot_id": str(conv.chatbot_id),
        "status": conv.status,
        "messages": [{"role": m.role, "content": m.content, "nlp_result": m.nlp_result, "created_at": m.created_at.isoformat()} for m in conv.messages],
        "created_at": conv.created_at.isoformat(),
    }


@router.post("/conversations/{conversation_id}/summary")
async def create_summary(conversation_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    messages = [{"role": m.role, "content": m.content} for m in conv.messages]
    summary_text = await nlp_service.generate_summary(messages)
    s = ConversationSummary(conversation_id=conversation_id, summary=summary_text)
    db.add(s)
    db.commit()
    return {"summary": summary_text}


# NLP endpoint
nlp_router = APIRouter(prefix="/api/nlp", tags=["nlp"])


@nlp_router.post("/analyze", response_model=NLPAnalyzeResponse)
async def analyze(payload: NLPAnalyzeRequest, _: User = Depends(get_current_user)):
    result = await nlp_service.analyze(payload.text)
    return result
