"""
Database migrations and initialization orchestrator.
Runs Alembic migrations and seeds the database/Pinecone.
Run: python scripts/init_db.py
"""
import sys
import os

# Put backend root in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.database import init_db
import scripts.seed_welfare_schemes as seed_welfare_schemes
import scripts.seed_sample_jobs as seed_sample_jobs

from alembic.config import Config
from alembic import command
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting database initialization...")

    # 1. Run migrations
    logger.info("Running Alembic migrations (upgrade head)...")
    try:
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_ini_path = os.path.join(backend_dir, "alembic.ini")
        
        if os.path.exists(alembic_ini_path):
            alembic_cfg = Config(alembic_ini_path)
            command.upgrade(alembic_cfg, "head")
            logger.info("✅ Database migrations completed successfully!")
        else:
            logger.warning("alembic.ini not found. Falling back to init_db() metadata creation.")
            init_db()
    except Exception as e:
        logger.error(f"❌ Alembic migration failed: {e}. Attempting init_db() fallback.")
        try:
            init_db()
            logger.info("✅ Fallback database table creation completed successfully!")
        except Exception as ex:
            logger.error(f"❌ Fallback database initialization failed: {ex}")
            sys.exit(1)

    # 2. Seed data
    logger.info("Starting data seeding...")
    try:
        logger.info("Seeding welfare schemes...")
        seed_welfare_schemes.main()
        
        logger.info("Seeding sample jobs...")
        seed_sample_jobs.main()
        
        logger.info("✅ Database initialization and seeding completed successfully!")
    except Exception as e:
        logger.error(f"❌ Data seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
