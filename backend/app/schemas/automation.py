from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AutomationPackageCreate(BaseModel):
    name: str
    description: Optional[str] = None
    language: str = "python"
    source_code: Optional[str] = None


class AutomationPackageResponse(AutomationPackageCreate):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AutomationRunResponse(BaseModel):
    id: UUID
    package_id: UUID
    status: str
    exit_code: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AutomationRunLogResponse(BaseModel):
    id: UUID
    run_id: UUID
    level: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SecurityValidationResponse(BaseModel):
    id: UUID
    package_id: UUID
    risk_level: str
    issues: list
    validated_at: datetime

    model_config = {"from_attributes": True}
