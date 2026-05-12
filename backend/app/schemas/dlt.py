from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DLTNetworkCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DLTNetworkResponse(DLTNetworkCreate):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DLTServerCreate(BaseModel):
    name: str
    endpoint: str


class DLTServerResponse(DLTServerCreate):
    id: UUID
    network_id: UUID
    is_active: bool

    model_config = {"from_attributes": True}


class SmartContractFieldCreate(BaseModel):
    name: str
    field_type: str
    required: bool = False


class SmartContractCreate(BaseModel):
    name: str
    description: Optional[str] = None
    fields: list[SmartContractFieldCreate] = []


class SmartContractResponse(BaseModel):
    id: UUID
    network_id: UUID
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DLTCredentialCreate(BaseModel):
    name: str
    allowed_routes: list[str] = []


class DLTCredentialResponse(BaseModel):
    id: UUID
    network_id: UUID
    name: str
    access_key: str
    allowed_routes: list[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DLTCredentialWithSecret(DLTCredentialResponse):
    secret_key: str


class DLTRecordResponse(BaseModel):
    id: UUID
    network_id: Optional[UUID]
    contract_id: Optional[UUID]
    event_type: str
    payload: dict
    record_hash: str
    created_at: datetime

    model_config = {"from_attributes": True}
