from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import generate_api_key_pair, hash_secret_key
from app.db.session import get_db
from app.models.dlt import (
    DLTCredential, DLTNetwork, DLTRecord, DLTServer,
    SmartContract, SmartContractField, SmartContractWorkflowBinding,
)
from app.models.user import User
from app.schemas.dlt import (
    DLTCredentialCreate, DLTCredentialResponse, DLTCredentialWithSecret,
    DLTNetworkCreate, DLTNetworkResponse, DLTRecordResponse,
    DLTServerCreate, DLTServerResponse,
    SmartContractCreate, SmartContractResponse,
)

router = APIRouter(prefix="/api/dlt", tags=["dlt"])


@router.get("/networks", response_model=List[DLTNetworkResponse])
def list_networks(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(DLTNetwork).all()


@router.post("/networks", response_model=DLTNetworkResponse, status_code=201)
def create_network(payload: DLTNetworkCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    net = DLTNetwork(**payload.model_dump())
    db.add(net)
    db.commit()
    db.refresh(net)
    return net


@router.post("/networks/{network_id}/servers", response_model=DLTServerResponse, status_code=201)
def add_server(network_id: UUID, payload: DLTServerCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    server = DLTServer(**payload.model_dump(), network_id=network_id)
    db.add(server)
    db.commit()
    db.refresh(server)
    return server


@router.get("/networks/{network_id}/contracts", response_model=List[SmartContractResponse])
def list_contracts(network_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(SmartContract).filter(SmartContract.network_id == network_id).all()


@router.post("/networks/{network_id}/contracts", response_model=SmartContractResponse, status_code=201)
def create_contract(network_id: UUID, payload: SmartContractCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    contract = SmartContract(name=payload.name, description=payload.description, network_id=network_id)
    db.add(contract)
    db.flush()
    for f in payload.fields:
        field = SmartContractField(**f.model_dump(), contract_id=contract.id)
        db.add(field)
    db.commit()
    db.refresh(contract)
    return contract


class BindWorkflowRequest(BaseModel):
    workflow_id: UUID


@router.post("/contracts/{contract_id}/bind-workflow", status_code=201)
def bind_workflow(contract_id: UUID, payload: BindWorkflowRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    workflow_id = payload.workflow_id
    binding = SmartContractWorkflowBinding(contract_id=contract_id, workflow_id=workflow_id)
    db.add(binding)
    db.commit()
    return {"status": "ok"}


# Credentials (accessKey/secretKey)
@router.post("/networks/{network_id}/credentials", response_model=DLTCredentialWithSecret, status_code=201)
def create_credential(network_id: UUID, payload: DLTCredentialCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    access_key, secret_key = generate_api_key_pair()
    cred = DLTCredential(
        network_id=network_id,
        name=payload.name,
        access_key=access_key,
        secret_key_hash=hash_secret_key(secret_key),
        allowed_routes=payload.allowed_routes,
    )
    db.add(cred)
    db.commit()
    db.refresh(cred)
    return {**DLTCredentialResponse.model_validate(cred).model_dump(), "secret_key": secret_key}


@router.get("/networks/{network_id}/credentials", response_model=List[DLTCredentialResponse])
def list_credentials(network_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(DLTCredential).filter(DLTCredential.network_id == network_id).all()


# Records
@router.get("/records", response_model=List[DLTRecordResponse])
def list_records(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(DLTRecord).order_by(DLTRecord.created_at.desc()).limit(100).all()


@router.get("/records/{record_hash}", response_model=DLTRecordResponse)
def get_record(record_hash: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    record = db.query(DLTRecord).filter(DLTRecord.record_hash == record_hash).first()
    if not record:
        raise HTTPException(404, "Record not found")
    return record


@router.get("/networks/{network_id}/records", response_model=List[DLTRecordResponse])
def network_records(network_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(DLTRecord).filter(DLTRecord.network_id == network_id).order_by(DLTRecord.created_at.desc()).all()
