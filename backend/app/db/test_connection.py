import sys
import os
from decimal import Decimal

# Add backend directory to python path dynamically
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../")
    )
)

from app.core.logging import setup_logging, logger
from app.core.database import SessionLocal, engine
from app.models.market_gig import MarketGig
from app.models.prediction_log import PredictionLog

def test_db_ops():
    setup_logging()
    logger.info("Starting database verification test...")
    
    db = SessionLocal()
    try:
        # 1. Insert a test gig listing
        logger.info("Inserting test market gig entry...")
        test_gig = MarketGig(
            platform="Upwork",
            primary_tech="Python",
            project_type="Machine Learning Ingestion API",
            complexity_level="High",
            estimated_hours=Decimal("40.00"),
            urgency="Urgent",
            has_auth=True,
            has_third_party_apis=True,
            actual_payout=Decimal("2500.00")
        )
        db.add(test_gig)
        
        # 2. Insert a test prediction log
        logger.info("Inserting test prediction log entry...")
        test_log = PredictionLog(
            primary_tech="Python",
            project_type="Machine Learning Ingestion API",
            complexity_level="High",
            estimated_hours=Decimal("40.00"),
            predicted_rate=Decimal("60.00"),
            ip_address="127.0.0.1"
        )
        db.add(test_log)
        
        # Commit the transaction
        db.commit()
        logger.info("Transaction committed successfully.")
        
        # 3. Query the entries to verify
        logger.info("Verifying inserted records...")
        queried_gig = db.query(MarketGig).filter_by(platform="Upwork").first()
        if queried_gig:
            logger.info(f"Verified Gig: {queried_gig}")
            assert queried_gig.primary_tech == "Python"
            assert queried_gig.actual_payout == Decimal("2500.00")
        else:
            raise ValueError("Test gig not found in database!")

        queried_log = db.query(PredictionLog).filter_by(ip_address="127.0.0.1").first()
        if queried_log:
            logger.info(f"Verified Prediction Log: {queried_log}")
            assert queried_log.primary_tech == "Python"
            assert queried_log.predicted_rate == Decimal("60.00")
        else:
            raise ValueError("Test prediction log not found in database!")
            
        # Clean up the test database entries
        logger.info("Cleaning up verification test entries...")
        db.delete(queried_gig)
        db.delete(queried_log)
        db.commit()
        logger.info("Database validation test PASSED successfully!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Database validation test FAILED: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    test_db_ops()
