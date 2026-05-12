from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.workflow import (
    Workflow, WorkflowForm, WorkflowFormField, WorkflowManager,
    WorkflowSLA, WorkflowStarter, WorkflowStep, WorkflowStepResponsible,
)
from app.schemas.workflow import (
    ResponsibleCreate, StarterManagerCreate,
    WorkflowCreate, WorkflowFormCreate, WorkflowFormResponse,
    WorkflowResponse, WorkflowSLACreate, WorkflowSLAResponse,
    WorkflowStepCreate, WorkflowStepResponse, WorkflowUpdate, WorkflowStepUpdate,
)

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.get("", response_model=List[WorkflowResponse])
def list_workflows(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Workflow).all()


@router.post("", response_model=WorkflowResponse, status_code=201)
def create_workflow(payload: WorkflowCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wf = Workflow(**payload.model_dump(), created_by=current_user.id)
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(404, "Workflow not found")
    return wf


@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(workflow_id: UUID, payload: WorkflowUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(404, "Workflow not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(wf, k, v)
    db.commit()
    db.refresh(wf)
    return wf


@router.delete("/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(404, "Workflow not found")
    db.delete(wf)
    db.commit()


# Steps
@router.get("/{workflow_id}/steps", response_model=List[WorkflowStepResponse])
def list_steps(workflow_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(WorkflowStep).filter(WorkflowStep.workflow_id == workflow_id).order_by(WorkflowStep.order).all()


@router.post("/{workflow_id}/steps", response_model=WorkflowStepResponse, status_code=201)
def create_step(workflow_id: UUID, payload: WorkflowStepCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    step = WorkflowStep(**payload.model_dump(), workflow_id=workflow_id)
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


@router.put("/{workflow_id}/steps/{step_id}", response_model=WorkflowStepResponse)
def update_step(workflow_id: UUID, step_id: UUID, payload: WorkflowStepUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    step = db.query(WorkflowStep).filter(WorkflowStep.id == step_id, WorkflowStep.workflow_id == workflow_id).first()
    if not step:
        raise HTTPException(404, "Step not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(step, k, v)
    db.commit()
    db.refresh(step)
    return step


@router.delete("/{workflow_id}/steps/{step_id}", status_code=204)
def delete_step(workflow_id: UUID, step_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    step = db.query(WorkflowStep).filter(WorkflowStep.id == step_id, WorkflowStep.workflow_id == workflow_id).first()
    if not step:
        raise HTTPException(404, "Step not found")
    db.delete(step)
    db.commit()


# SLA
@router.post("/{workflow_id}/steps/{step_id}/sla", response_model=WorkflowSLAResponse, status_code=201)
def set_sla(workflow_id: UUID, step_id: UUID, payload: WorkflowSLACreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    existing = db.query(WorkflowSLA).filter(WorkflowSLA.step_id == step_id).first()
    if existing:
        existing.deadline_hours = payload.deadline_hours
        existing.warning_hours = payload.warning_hours
        db.commit()
        db.refresh(existing)
        return existing
    sla = WorkflowSLA(**payload.model_dump(), step_id=step_id)
    db.add(sla)
    db.commit()
    db.refresh(sla)
    return sla


# Starters & Managers
@router.post("/{workflow_id}/starters", status_code=201)
def add_starter(workflow_id: UUID, payload: StarterManagerCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    s = WorkflowStarter(**payload.model_dump(), workflow_id=workflow_id)
    db.add(s)
    db.commit()
    return {"status": "ok"}


@router.post("/{workflow_id}/managers", status_code=201)
def add_manager(workflow_id: UUID, payload: StarterManagerCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    m = WorkflowManager(**payload.model_dump(), workflow_id=workflow_id)
    db.add(m)
    db.commit()
    return {"status": "ok"}


# Responsibles
@router.post("/{workflow_id}/steps/{step_id}/responsibles", status_code=201)
def add_responsible(workflow_id: UUID, step_id: UUID, payload: ResponsibleCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    r = WorkflowStepResponsible(**payload.model_dump(), step_id=step_id)
    db.add(r)
    db.commit()
    return {"status": "ok"}


# Forms
@router.get("/{workflow_id}/forms", response_model=List[WorkflowFormResponse])
def list_forms(workflow_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(WorkflowForm).filter(WorkflowForm.workflow_id == workflow_id).all()


@router.post("/{workflow_id}/forms", response_model=WorkflowFormResponse, status_code=201)
def create_form(workflow_id: UUID, payload: WorkflowFormCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    form = WorkflowForm(
        workflow_id=workflow_id,
        step_id=payload.step_id,
        name=payload.name,
        schema=payload.schema,
    )
    db.add(form)
    db.flush()
    for i, f in enumerate(payload.fields):
        field = WorkflowFormField(**f.model_dump(), form_id=form.id, order=i)
        db.add(field)
    db.commit()
    db.refresh(form)
    return form


# Kanban
@router.get("/{workflow_id}/kanban")
def get_kanban(workflow_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from app.models.process import ProcessInstance
    steps = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == workflow_id).order_by(WorkflowStep.order).all()
    result = []
    for step in steps:
        processes = db.query(ProcessInstance).filter(
            ProcessInstance.workflow_id == workflow_id,
            ProcessInstance.current_step_id == step.id,
            ProcessInstance.status == "active",
        ).all()
        result.append({
            "step": {"id": str(step.id), "name": step.name, "order": step.order, "is_final": step.is_final},
            "processes": [
                {
                    "id": str(p.id),
                    "title": p.title,
                    "status": p.status,
                    "created_at": p.created_at.isoformat(),
                }
                for p in processes
            ],
        })
    return result
