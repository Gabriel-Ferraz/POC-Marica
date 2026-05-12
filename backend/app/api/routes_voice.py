from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.voice import VoiceBot, VoiceCall, VoiceCallTranscript, VoiceCampaign
from app.schemas.voice import VoiceBotCreate, VoiceBotResponse, VoiceCampaignCreate, VoiceCampaignResponse
from app.services import nlp_service, voice_service

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.get("/bots", response_model=List[VoiceBotResponse])
def list_bots(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(VoiceBot).all()


@router.post("/bots", response_model=VoiceBotResponse, status_code=201)
def create_bot(payload: VoiceBotCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    bot = VoiceBot(**payload.model_dump())
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot


@router.post("/call")
async def voice_call(audio: UploadFile = File(...), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    import uuid
    audio_bytes = await audio.read()
    text = await voice_service.speech_to_text(audio_bytes, audio.content_type or "audio/wav")
    nlp_result = await nlp_service.analyze(text)
    response_text = nlp_result.get("response", "Olá! Como posso ajudá-lo?")
    audio_response = await voice_service.text_to_speech(response_text)

    call = VoiceCall(session_id=str(uuid.uuid4()))
    db.add(call)
    db.flush()

    db.add(VoiceCallTranscript(call_id=call.id, role="user", text=text))
    db.add(VoiceCallTranscript(call_id=call.id, role="assistant", text=response_text))
    db.commit()

    return Response(content=audio_response, media_type="audio/wav", headers={
        "X-Transcript-User": text,
        "X-Transcript-Assistant": response_text,
        "X-NLP-Intent": nlp_result.get("intent", ""),
    })


class TextCallRequest(BaseModel):
    text: str


@router.post("/call/text")
async def voice_call_text(payload: TextCallRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    import uuid
    text = payload.text
    nlp_result = await nlp_service.analyze(text)
    response_text = nlp_result.get("response", "Olá! Como posso ajudá-lo?")
    call = VoiceCall(session_id=str(uuid.uuid4()))
    db.add(call)
    db.flush()
    db.add(VoiceCallTranscript(call_id=call.id, role="user", text=text))
    db.add(VoiceCallTranscript(call_id=call.id, role="assistant", text=response_text))
    db.commit()
    return {"user_text": text, "assistant_text": response_text, "nlp_result": nlp_result}


# Campaigns
@router.get("/campaigns", response_model=List[VoiceCampaignResponse])
def list_campaigns(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(VoiceCampaign).all()


@router.post("/campaigns", response_model=VoiceCampaignResponse, status_code=201)
def create_campaign(payload: VoiceCampaignCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    campaign = VoiceCampaign(**payload.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign
