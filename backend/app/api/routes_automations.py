from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.automation import AutomationPackage, AutomationRun, AutomationRunLog, AutomationSecurityValidation
from app.models.user import User
from app.schemas.automation import (
    AutomationPackageCreate, AutomationPackageResponse,
    AutomationRunLogResponse, AutomationRunResponse, SecurityValidationResponse,
)
from app.services import automation_service

router = APIRouter(prefix="/api/automations", tags=["automations"])


@router.get("", response_model=List[AutomationPackageResponse])
def list_packages(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(AutomationPackage).all()


@router.post("", response_model=AutomationPackageResponse, status_code=201)
def create_package(payload: AutomationPackageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pkg = AutomationPackage(**payload.model_dump(), uploaded_by=current_user.id)
    db.add(pkg)
    db.commit()
    db.refresh(pkg)
    return pkg


@router.get("/{package_id}", response_model=AutomationPackageResponse)
def get_package(package_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    pkg = db.query(AutomationPackage).filter(AutomationPackage.id == package_id).first()
    if not pkg:
        raise HTTPException(404, "Package not found")
    return pkg


@router.post("/{package_id}/run", response_model=AutomationRunResponse, status_code=201)
def run_automation(package_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pkg = db.query(AutomationPackage).filter(AutomationPackage.id == package_id).first()
    if not pkg:
        raise HTTPException(404, "Package not found")
    run = AutomationRun(package_id=package_id, triggered_by=current_user.id)
    db.add(run)
    db.flush()
    run.package = pkg
    return automation_service.execute_automation(db, run)


@router.get("/{package_id}/runs", response_model=List[AutomationRunResponse])
def list_runs(package_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(AutomationRun).filter(AutomationRun.package_id == package_id).all()


@router.get("/runs/{run_id}/logs", response_model=List[AutomationRunLogResponse])
def get_logs(run_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(AutomationRunLog).filter(AutomationRunLog.run_id == run_id).order_by(AutomationRunLog.created_at).all()


@router.post("/{package_id}/security-review", response_model=SecurityValidationResponse, status_code=201)
def security_review(package_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    pkg = db.query(AutomationPackage).filter(AutomationPackage.id == package_id).first()
    if not pkg:
        raise HTTPException(404, "Package not found")
    result = automation_service.analyze_security(pkg.source_code or "")
    validation = AutomationSecurityValidation(
        package_id=package_id,
        risk_level=result["risk_level"],
        issues=result["issues"],
    )
    db.add(validation)
    db.commit()
    db.refresh(validation)
    return validation
