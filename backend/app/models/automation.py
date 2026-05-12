import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def now_utc():
    return datetime.now(timezone.utc)


class AutomationPackage(Base):
    __tablename__ = "automation_packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    language = Column(String(50), nullable=False, default="python")  # python, java, dotnet
    file_path = Column(String(500), nullable=True)
    source_code = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    runs = relationship("AutomationRun", back_populates="package")
    security_validations = relationship("AutomationSecurityValidation", back_populates="package")


class AutomationRun(Base):
    __tablename__ = "automation_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = Column(UUID(as_uuid=True), ForeignKey("automation_packages.id"), nullable=False)
    triggered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    exit_code = Column(String(10), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    celery_task_id = Column(String(100), nullable=True)

    package = relationship("AutomationPackage", back_populates="runs")
    logs = relationship("AutomationRunLog", back_populates="run", cascade="all, delete-orphan")


class AutomationRunLog(Base):
    __tablename__ = "automation_run_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("automation_runs.id"), nullable=False)
    level = Column(String(20), default="info")  # info, warning, error
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    run = relationship("AutomationRun", back_populates="logs")


class AutomationSecurityValidation(Base):
    __tablename__ = "automation_security_validations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = Column(UUID(as_uuid=True), ForeignKey("automation_packages.id"), nullable=False)
    risk_level = Column(String(20), default="unknown")  # low, medium, high, unknown
    issues = Column(JSON, default=list)
    validated_at = Column(DateTime(timezone=True), default=now_utc)

    package = relationship("AutomationPackage", back_populates="security_validations")
