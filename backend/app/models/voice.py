import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def now_utc():
    return datetime.now(timezone.utc)


class VoiceBot(Base):
    __tablename__ = "voice_bots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    calls = relationship("VoiceCall", back_populates="bot")


class VoiceCall(Base):
    __tablename__ = "voice_calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_id = Column(UUID(as_uuid=True), ForeignKey("voice_bots.id"), nullable=True)
    session_id = Column(String(100))
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=now_utc)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    bot = relationship("VoiceBot", back_populates="calls")
    transcripts = relationship("VoiceCallTranscript", back_populates="call")


class VoiceCallTranscript(Base):
    __tablename__ = "voice_call_transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("voice_calls.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    text = Column(Text, nullable=False)
    audio_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    call = relationship("VoiceCall", back_populates="transcripts")


class VoiceCampaign(Base):
    __tablename__ = "voice_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="draft")  # draft, active, paused, completed
    scheduled_start = Column(DateTime(timezone=True), nullable=True)
    ideal_hours = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    targets = relationship("VoiceCampaignTarget", back_populates="campaign", cascade="all, delete-orphan")
    scripts = relationship("VoiceCampaignScript", back_populates="campaign", cascade="all, delete-orphan")
    rules = relationship("VoiceCampaignRule", back_populates="campaign", cascade="all, delete-orphan")


class VoiceCampaignTarget(Base):
    __tablename__ = "voice_campaign_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("voice_campaigns.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255))
    phone = Column(String(50))
    metadata = Column(JSON, default=dict)

    campaign = relationship("VoiceCampaign", back_populates="targets")


class VoiceCampaignScript(Base):
    __tablename__ = "voice_campaign_scripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("voice_campaigns.id", ondelete="CASCADE"), nullable=False)
    step_order = Column(String(10), default="1")
    content = Column(Text, nullable=False)
    is_dynamic = Column(Boolean, default=False)

    campaign = relationship("VoiceCampaign", back_populates="scripts")


class VoiceCampaignRule(Base):
    __tablename__ = "voice_campaign_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("voice_campaigns.id", ondelete="CASCADE"), nullable=False)
    rule_type = Column(String(100), nullable=False)
    config = Column(JSON, default=dict)

    campaign = relationship("VoiceCampaign", back_populates="rules")
