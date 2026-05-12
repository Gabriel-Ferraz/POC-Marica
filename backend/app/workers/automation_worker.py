from app.workers.celery_app import celery_app


@celery_app.task(name="automation.run")
def run_automation_task(run_id: str):
    from app.db.session import SessionLocal
    from app.models.automation import AutomationRun
    from app.services import automation_service
    import uuid

    db = SessionLocal()
    try:
        run = db.query(AutomationRun).filter(AutomationRun.id == uuid.UUID(run_id)).first()
        if not run:
            return {"error": "Run not found"}
        automation_service.execute_automation(db, run)
        return {"status": run.status}
    finally:
        db.close()
