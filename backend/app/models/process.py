import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def now_utc():
    return datetime.now(timezone.utc)


class ProcessInstance(Base):
    __tablename__ = "process_instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    current_step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_steps.id"), nullable=True)
    started_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="active")  # active, completed, cancelled
    form_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    workflow = relationship("Workflow", back_populates="instances")
    activities = relationship("ProcessActivity", back_populates="process", order_by="ProcessActivity.created_at")
    attachments = relationship("ProcessAttachment", back_populates="process")
    signatures = relationship("ProcessSignature", back_populates="process")


class ProcessActivity(Base):
    __tablename__ = "process_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("process_instances.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # accept, return, comment, sign
    from_step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_steps.id"), nullable=True)
    to_step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_steps.id"), nullable=True)
    comment = Column(Text)
    dlt_hash = Column(String(64))
    created_at = Column(DateTime(timezone=True), default=now_utc)

    process = relationship("ProcessInstance", back_populates="activities")


class ProcessAttachment(Base):
    __tablename__ = "process_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("process_instances.id"), nullable=False)
    field_id = Column(String(100))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100))
    is_signature_attachment = Column(Boolean, default=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=now_utc)

    process = relationship("ProcessInstance", back_populates="attachments")
    signature = relationship("ProcessSignature", back_populates="attachment", uselist=False)


class ProcessSignature(Base):
    __tablename__ = "process_signatures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("process_instances.id"), nullable=False)
    attachment_id = Column(UUID(as_uuid=True), ForeignKey("process_attachments.id"), nullable=True)
    status = Column(String(50), default="pending")  # pending, in_progress, completed
    signers = Column(JSON, default=list)  # list of {user_id, signed_at, signature_hash}
    required_signers_count = Column(String(10), default="1")
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    process = relationship("ProcessInstance", back_populates="signatures")
    attachment = relationship("ProcessAttachment", back_populates="signature")
