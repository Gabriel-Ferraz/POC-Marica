from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.process import ProcessActivity, ProcessInstance
from app.models.workflow import Workflow, WorkflowStep
from app.services import dlt_service


def get_next_step(db: Session, workflow_id: UUID, current_step_id: UUID | None) -> WorkflowStep | None:
    steps = (
        db.query(WorkflowStep)
        .filter(WorkflowStep.workflow_id == workflow_id)
        .order_by(WorkflowStep.order)
        .all()
    )
    if not steps:
        return None
    if current_step_id is None:
        return steps[0]
    for i, step in enumerate(steps):
        if step.id == current_step_id and i + 1 < len(steps):
            return steps[i + 1]
    return None


def get_previous_step(db: Session, workflow_id: UUID, current_step_id: UUID | None) -> WorkflowStep | None:
    steps = (
        db.query(WorkflowStep)
        .filter(WorkflowStep.workflow_id == workflow_id)
        .order_by(WorkflowStep.order)
        .all()
    )
    for i, step in enumerate(steps):
        if step.id == current_step_id and i > 0:
            return steps[i - 1]
    return None


def accept_process(db: Session, process: ProcessInstance, user_id: UUID, comment: str | None = None) -> ProcessInstance:
    from_step_id = process.current_step_id
    next_step = get_next_step(db, process.workflow_id, from_step_id)

    activity_payload = {
        "from_step_id": str(from_step_id) if from_step_id else None,
        "to_step_id": str(next_step.id) if next_step else None,
        "user_id": str(user_id),
        "action": "accept",
    }
    dlt_record = dlt_service.record_event(
        db=db,
        event_type="PROCESS_ACCEPTED",
        payload=activity_payload,
        workflow_id=process.workflow_id,
        process_id=process.id,
    )

    activity = ProcessActivity(
        process_id=process.id,
        user_id=user_id,
        action="accept",
        from_step_id=from_step_id,
        to_step_id=next_step.id if next_step else None,
        comment=comment,
        dlt_hash=dlt_record.record_hash,
    )
    db.add(activity)

    if next_step:
        process.current_step_id = next_step.id
        if next_step.is_final:
            process.status = "completed"
            process.completed_at = datetime.now(timezone.utc)
    else:
        process.status = "completed"
        process.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(process)
    return process


def return_process(db: Session, process: ProcessInstance, user_id: UUID, comment: str | None = None) -> ProcessInstance:
    from_step_id = process.current_step_id
    prev_step = get_previous_step(db, process.workflow_id, from_step_id)

    activity_payload = {
        "from_step_id": str(from_step_id) if from_step_id else None,
        "to_step_id": str(prev_step.id) if prev_step else None,
        "user_id": str(user_id),
        "action": "return",
        "comment": comment,
    }
    dlt_record = dlt_service.record_event(
        db=db,
        event_type="PROCESS_RETURNED",
        payload=activity_payload,
        workflow_id=process.workflow_id,
        process_id=process.id,
    )

    activity = ProcessActivity(
        process_id=process.id,
        user_id=user_id,
        action="return",
        from_step_id=from_step_id,
        to_step_id=prev_step.id if prev_step else from_step_id,
        comment=comment,
        dlt_hash=dlt_record.record_hash,
    )
    db.add(activity)

    if prev_step:
        process.current_step_id = prev_step.id

    db.commit()
    db.refresh(process)
    return process
