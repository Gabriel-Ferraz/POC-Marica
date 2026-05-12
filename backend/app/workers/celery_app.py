from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "poc_ictim",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.idp_worker", "app.workers.automation_worker", "app.workers.notification_worker"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
)
