import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def now_utc():
    return datetime.now(timezone.utc)


class DLTNetwork(Base):
    __tablename__ = "dlt_networks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    servers = relationship("DLTServer", back_populates="network", cascade="all, delete-orphan")
    contracts = relationship("SmartContract", back_populates="network")
    credentials = relationship("DLTCredential", back_populates="network", cascade="all, delete-orphan")
    records = relationship("DLTRecord", back_populates="network")


class DLTServer(Base):
    __tablename__ = "dlt_servers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    network_id = Column(UUID(as_uuid=True), ForeignKey("dlt_networks.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    endpoint = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    network = relationship("DLTNetwork", back_populates="servers")


class SmartContract(Base):
    __tablename__ = "smart_contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    network_id = Column(UUID(as_uuid=True), ForeignKey("dlt_networks.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    network = relationship("DLTNetwork", back_populates="contracts")
    fields = relationship("SmartContractField", back_populates="contract", cascade="all, delete-orphan")
    workflow_bindings = relationship("SmartContractWorkflowBinding", back_populates="contract", cascade="all, delete-orphan")


class SmartContractField(Base):
    __tablename__ = "smart_contract_fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("smart_contracts.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    field_type = Column(String(50), nullable=False)  # text, number, boolean, date, time
    required = Column(Boolean, default=False)

    contract = relationship("SmartContract", back_populates="fields")


class SmartContractWorkflowBinding(Base):
    __tablename__ = "smart_contract_workflow_bindings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("smart_contracts.id", ondelete="CASCADE"), nullable=False)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)

    contract = relationship("SmartContract", back_populates="workflow_bindings")


class DLTCredential(Base):
    __tablename__ = "dlt_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    network_id = Column(UUID(as_uuid=True), ForeignKey("dlt_networks.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    access_key = Column(String(100), unique=True, nullable=False, index=True)
    secret_key_hash = Column(String(64), nullable=False)
    allowed_routes = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    network = relationship("DLTNetwork", back_populates="credentials")


class DLTRecord(Base):
    __tablename__ = "dlt_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    network_id = Column(UUID(as_uuid=True), ForeignKey("dlt_networks.id"), nullable=True)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("smart_contracts.id"), nullable=True)
    workflow_id = Column(UUID(as_uuid=True), nullable=True)
    process_id = Column(UUID(as_uuid=True), nullable=True)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, default=dict)
    record_hash = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    network = relationship("DLTNetwork", back_populates="records")


class DLTEndpointPermission(Base):
    __tablename__ = "dlt_endpoint_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credential_id = Column(UUID(as_uuid=True), ForeignKey("dlt_credentials.id", ondelete="CASCADE"), nullable=False)
    route_pattern = Column(String(500), nullable=False)
    methods = Column(JSON, default=list)
