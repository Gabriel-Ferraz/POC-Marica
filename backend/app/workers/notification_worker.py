from app.workers.celery_app import celery_app


@celery_app.task(name="notification.send")
def send_notification_task(user_id: str, title: str, body: str, notif_type: str = "info"):
    from app.db.session import SessionLocal
    from app.models.notification import Notification
    import uuid

    db = SessionLocal()
    try:
        notif = Notification(user_id=uuid.UUID(user_id), title=title, body=body, type=notif_type)
        db.add(notif)
        db.commit()
        return {"status": "sent"}
    finally:
        db.close()
