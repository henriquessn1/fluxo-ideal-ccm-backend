from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.services import HealthChecker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class BackgroundScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.health_checker = HealthChecker()
    
    async def health_check_job(self):
        """Job to run health checks on all clients"""
        async with AsyncSessionLocal() as db:
            try:
                await self.health_checker.check_all_clients(db)
                logger.info("Health check job completed successfully")
            except Exception as e:
                logger.error(f"Health check job failed: {str(e)}")
    
    def start(self):
        """Start the scheduler with configured jobs"""
        # Add health check job
        self.scheduler.add_job(
            self.health_check_job,
            trigger=IntervalTrigger(seconds=settings.HEALTH_CHECK_INTERVAL),
            id='health_check_job',
            name='Health Check Job',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Background scheduler started with health check interval: {settings.HEALTH_CHECK_INTERVAL}s")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Background scheduler stopped")