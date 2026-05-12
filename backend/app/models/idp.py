import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def now_utc():
    return datetime.now(timezone.utc)


class IDPDocument(Base):
    __tablename__ = "idp_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100))
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    jobs = relationship("IDPProcessingJob", back_populates="document", cascade="all, delete-orphan")
    result = relationship("IDPResult", back_populates="document", uselist=False)


class IDPProcessingJob(Base):
    __tablename__ = "idp_processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("idp_documents.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    celery_task_id = Column(String(100), nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    document = relationship("IDPDocument", back_populates="jobs")


class IDPResult(Base):
    __tablename__ = "idp_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("idp_documents.id"), unique=True, nullable=False)
    document_type = Column(String(100), nullable=True)
    confidence = Column(Float, default=0.0)
    raw_text = Column(Text)
    has_handwriting = Column(Boolean, default=False)
    json_export = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    document = relationship("IDPDocument", back_populates="result")
    extracted_fields = relationship("IDPExtractedField", back_populates="result", cascade="all, delete-orphan")


class IDPExtractedField(Base):
    __tablename__ = "idp_extracted_fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id = Column(UUID(as_uuid=True), ForeignKey("idp_results.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    field_value = Column(Text)
    confidence = Column(Float, default=0.0)

    result = relationship("IDPResult", back_populates="extracted_fields")
