import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def now_utc():
    return datetime.now(timezone.utc)


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    steps = relationship("WorkflowStep", back_populates="workflow", order_by="WorkflowStep.order", cascade="all, delete-orphan")
    forms = relationship("WorkflowForm", back_populates="workflow", cascade="all, delete-orphan")
    starters = relationship("WorkflowStarter", back_populates="workflow", cascade="all, delete-orphan")
    managers = relationship("WorkflowManager", back_populates="workflow", cascade="all, delete-orphan")
    instances = relationship("ProcessInstance", back_populates="workflow")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False, default=0)
    is_final = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    workflow = relationship("Workflow", back_populates="steps")
    responsibles = relationship("WorkflowStepResponsible", back_populates="step", cascade="all, delete-orphan")
    sla = relationship("WorkflowSLA", back_populates="step", uselist=False, cascade="all, delete-orphan")
    form = relationship("WorkflowForm", back_populates="step", uselist=False)


class WorkflowForm(Base):
    __tablename__ = "workflow_forms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_steps.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    schema = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    workflow = relationship("Workflow", back_populates="forms")
    step = relationship("WorkflowStep", back_populates="form")
    fields = relationship("WorkflowFormField", back_populates="form", cascade="all, delete-orphan")


class WorkflowFormField(Base):
    __tablename__ = "workflow_form_fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(UUID(as_uuid=True), ForeignKey("workflow_forms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(100), nullable=False)
    field_type = Column(String(50), nullable=False)
    label = Column(String(255), nullable=False)
    required = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    options = Column(JSON, default=dict)

    form = relationship("WorkflowForm", back_populates="fields")


class WorkflowStarter(Base):
    __tablename__ = "workflow_starters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)

    workflow = relationship("Workflow", back_populates="starters")


class WorkflowManager(Base):
    __tablename__ = "workflow_managers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)

    workflow = relationship("Workflow", back_populates="managers")


class WorkflowStepResponsible(Base):
    __tablename__ = "workflow_step_responsibles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_steps.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)

    step = relationship("WorkflowStep", back_populates="responsibles")


class WorkflowSLA(Base):
    __tablename__ = "workflow_slas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_steps.id", ondelete="CASCADE"), nullable=False, unique=True)
    deadline_hours = Column(Integer, nullable=False, default=24)
    warning_hours = Column(Integer, nullable=False, default=8)

    step = relationship("WorkflowStep", back_populates="sla")
