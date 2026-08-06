import sys
import os

# Add backend directory to python path dynamically
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../")
    )
)

from app.core.logging import setup_logging, logger
from app.core.database import engine, Base
# Import models to ensure they are registered on Base.metadata
from app.models import MarketGig, PredictionLog

def init_database() -> None:
    """Creates all database tables, columns, and indexes defined in SQLAlchemy metadata."""
    setup_logging()
    
    logger.info("Initializing database schema provisioning...")
    try:
        # Create all tables in the database
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized and all tables/indexes created successfully.")
    except Exception as e:
        logger.error(f"Error provisioning database schema: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    init_database()
