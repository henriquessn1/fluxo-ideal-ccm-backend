from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "monitoring",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks.health_check_tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'check-all-clients-health': {
        'task': 'app.tasks.health_check_tasks.check_all_clients_health',
        'schedule': settings.HEALTH_CHECK_INTERVAL,  # Every 30 seconds by default
    },
}

if __name__ == '__main__':
    celery_app.start()