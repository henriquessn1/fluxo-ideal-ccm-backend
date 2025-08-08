from celery import shared_task
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services import HealthChecker
from app.models import Client


@shared_task(name="app.tasks.health_check_tasks.check_all_clients_health")
def check_all_clients_health():
    """Celery task to check health of all clients"""
    db = SessionLocal()
    try:
        health_checker = HealthChecker()
        
        # Get all active clients
        clients = db.query(Client).filter(Client.is_active == True).all()
        
        for client in clients:
            check_client_health.delay(client.id)
        
        return f"Triggered health checks for {len(clients)} clients"
    finally:
        db.close()


@shared_task(name="app.tasks.health_check_tasks.check_client_health")
def check_client_health(client_id: int):
    """Celery task to check health of a specific client's services"""
    db = SessionLocal()
    try:
        health_checker = HealthChecker()
        health_checker.check_client_services_sync(db, client_id)
        return f"Health check completed for client {client_id}"
    except Exception as e:
        return f"Health check failed for client {client_id}: {str(e)}"
    finally:
        db.close()