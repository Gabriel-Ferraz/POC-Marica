from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class WorkflowResponse(WorkflowBase):
    id: UUID
    created_by: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkflowStepBase(BaseModel):
    name: str
    description: Optional[str] = None
    order: int = 0
    is_final: bool = False


class WorkflowStepCreate(WorkflowStepBase):
    pass


class WorkflowStepUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_final: Optional[bool] = None


class WorkflowStepResponse(WorkflowStepBase):
    id: UUID
    workflow_id: UUID

    model_config = {"from_attributes": True}


class WorkflowFormFieldBase(BaseModel):
    field_id: str
    field_type: str
    label: str
    required: bool = False
    order: int = 0
    options: dict = {}


class WorkflowFormCreate(BaseModel):
    name: str
    step_id: Optional[UUID] = None
    schema: dict = {}
    fields: list[WorkflowFormFieldBase] = []


class WorkflowFormResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    step_id: Optional[UUID]
    name: str
    schema: dict

    model_config = {"from_attributes": True}


class WorkflowSLACreate(BaseModel):
    deadline_hours: int = 24
    warning_hours: int = 8


class WorkflowSLAResponse(WorkflowSLACreate):
    id: UUID
    step_id: UUID

    model_config = {"from_attributes": True}


class StarterManagerCreate(BaseModel):
    user_id: Optional[UUID] = None
    department_id: Optional[UUID] = None


class ResponsibleCreate(BaseModel):
    user_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
