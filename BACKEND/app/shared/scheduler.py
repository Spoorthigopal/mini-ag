from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def run_job_sync():
    """Wrapper to run job sync with a new database session."""
    from app.database import SessionLocal
    from app.internships.service import sync_jobs_from_jsearch
    
    logger.info("Starting scheduled background job sync from JSearch...")
    db = SessionLocal()
    try:
        sync_jobs_from_jsearch(db)
        logger.info("✅ Scheduled background job sync completed successfully!")
    except Exception as e:
        logger.error(f"❌ Scheduled background job sync failed: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler and schedule daily jobs."""
    if not scheduler.running:
        # Schedule sync_jobs_from_jsearch daily at 2 AM
        scheduler.add_job(
            run_job_sync,
            CronTrigger(hour=2, minute=0),
            id="sync_jsearch_jobs",
            replace_existing=True
        )
        scheduler.start()
        logger.info("Background scheduler started and daily jobs scheduled.")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background scheduler stopped")


def add_cron_job(func, cron_expression: str, job_id: str):
    """Add a cron job to the scheduler.
    
    cron_expression: e.g. '0 2 * * *' for 2am daily
    """
    scheduler.add_job(
        func,
        CronTrigger.from_crontab(cron_expression),
        id=job_id,
        replace_existing=True
    )
    logger.info(f"Cron job '{job_id}' scheduled: {cron_expression}")
