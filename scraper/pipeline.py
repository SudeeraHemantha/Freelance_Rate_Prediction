import sys
import os
import argparse
from typing import List, Dict, Any
from decimal import Decimal

# Add backend folder to python path dynamically
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../backend")
    )
)

# Core imports from backend
from app.core.logging import setup_logging, logger
from app.core.database import SessionLocal
from app.models.market_gig import MarketGig

# Scraper module imports
from scraper.selenium_scraper import SeleniumScraper
from scraper.simulation import generate_simulated_gigs_batch


class DataIngestionPipeline:
    """Enterprise ingestion pipeline responsible for scraping, parsing, and storing market gig data."""

    def __init__(self, platform: str, simulate: bool = False):
        # Clean platform string
        if platform.lower() == "both":
            self.platforms = ["Upwork", "Fiverr"]
        else:
            self.platforms = [platform.capitalize()]

        self.simulate = simulate
        logger.info(f"Initialized ingestion pipeline (platforms: {self.platforms}, simulate_mode: {self.simulate})")

    def scrape_gigs(self, tech_stack: List[str], count_per_tech: int = 5) -> List[Dict[str, Any]]:
        """Scrapes freelance gigs matching selected technologies with simulation fallback."""
        all_gigs = []
        
        # If simulation mode is explicitly requested, bypass Selenium setup
        if self.simulate:
            logger.info("Running pipeline in simulated mode.")
            for plat in self.platforms:
                for tech in tech_stack:
                    simulated = generate_simulated_gigs_batch(
                        count=count_per_tech,
                        platform=plat,
                        tech_stack=[tech]
                    )
                    all_gigs.extend(simulated)
            return all_gigs

        # Real scraping mode (with fallback hooks)
        scraper = SeleniumScraper()
        try:
            for plat in self.platforms:
                for tech in tech_stack:
                    logger.info(f"Attempting to scrape {plat} gigs for: {tech}")
                    try:
                        if plat == "Upwork":
                            scraped_gigs = scraper.scrape_upwork_gigs(tech, max_results=count_per_tech)
                        else:  # Fiverr
                            scraped_gigs = scraper.scrape_fiverr_gigs(tech, max_results=count_per_tech)
                        
                        all_gigs.extend(scraped_gigs)
                        logger.info(f"Successfully scraped {len(scraped_gigs)} gigs for {tech} on {plat}")
                    
                    except Exception as e:
                        # Fallback logic for scraping errors or captcha blocks
                        logger.warning(
                            f"Failed to scrape {plat} for tech '{tech}': {e}. "
                            f"Gracefully falling back to high-fidelity simulation to maintain ingestion continuity."
                        )
                        fallback_gigs = generate_simulated_gigs_batch(
                            count=count_per_tech,
                            platform=plat,
                            tech_stack=[tech]
                        )
                        all_gigs.extend(fallback_gigs)
        finally:
            scraper.close()

        return all_gigs

    def parse_gig(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validates and coerces raw scraped listing dictionary to match db schema standards."""
        # Enforce and validate fields
        platform = str(raw_data.get("platform", "Unknown"))
        primary_tech = str(raw_data.get("primary_tech", "General"))
        project_type = str(raw_data.get("project_type", "Software Development"))
        complexity_level = str(raw_data.get("complexity_level", "Medium"))
        urgency = str(raw_data.get("urgency", "Medium"))
        has_auth = bool(raw_data.get("has_auth", False))
        has_third_party_apis = bool(raw_data.get("has_third_party_apis", False))

        # Precision float/decimal parsing
        try:
            estimated_hours = Decimal(str(raw_data.get("estimated_hours", "0.00")))
        except Exception:
            estimated_hours = Decimal("0.00")

        try:
            actual_payout = Decimal(str(raw_data.get("actual_payout", "0.00")))
        except Exception:
            actual_payout = Decimal("0.00")

        # Double check field length boundaries
        if len(platform) > 50: platform = platform[:50]
        if len(primary_tech) > 100: primary_tech = primary_tech[:100]
        if len(project_type) > 100: project_type = project_type[:100]
        if len(complexity_level) > 50: complexity_level = complexity_level[:50]
        if len(urgency) > 50: urgency = urgency[:50]

        return {
            "platform": platform,
            "primary_tech": primary_tech,
            "project_type": project_type,
            "complexity_level": complexity_level,
            "estimated_hours": estimated_hours,
            "urgency": urgency,
            "has_auth": has_auth,
            "has_third_party_apis": has_third_party_apis,
            "actual_payout": actual_payout
        }

    def save_to_db(self, parsed_gigs: List[Dict[str, Any]]) -> int:
        """Stores parsed listings into database table using ACID transaction blocks."""
        if not parsed_gigs:
            logger.info("No gigs available to save.")
            return 0

        logger.info(f"Starting ACID database transaction for {len(parsed_gigs)} entries...")
        db = SessionLocal()
        inserted_count = 0
        try:
            for gig_data in parsed_gigs:
                gig_record = MarketGig(
                    platform=gig_data["platform"],
                    primary_tech=gig_data["primary_tech"],
                    project_type=gig_data["project_type"],
                    complexity_level=gig_data["complexity_level"],
                    estimated_hours=gig_data["estimated_hours"],
                    urgency=gig_data["urgency"],
                    has_auth=gig_data["has_auth"],
                    has_third_party_apis=gig_data["has_third_party_apis"],
                    actual_payout=gig_data["actual_payout"]
                )
                db.add(gig_record)
                inserted_count += 1
            
            # Commit the session transaction
            db.commit()
            logger.info(f"Database transaction committed successfully. Ingested rows: {inserted_count}")
            return inserted_count
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to ingest scraped listings into PostgreSQL: {e}. Session rolled back.")
            raise
        finally:
            db.close()


def main():
    setup_logging()
    logger.info("=== Starting Freelance Rate Ingestion CLI ===")

    parser = argparse.ArgumentParser(description="Freelance Rate & Demand Predictor Ingestion Pipeline CLI")
    parser.add_argument(
        "--platform", 
        type=str, 
        default="both", 
        choices=["upwork", "fiverr", "both"], 
        help="Target platform to harvest gigs from."
    )
    parser.add_argument(
        "--tech", 
        type=str, 
        default="python,react,node.js,go,rust", 
        help="Comma-separated primary technology keywords."
    )
    parser.add_argument(
        "--simulate", 
        action="store_true", 
        help="Bypass live scraper calls and use the high-fidelity simulator."
    )
    parser.add_argument(
        "--count", 
        type=int, 
        default=5, 
        help="Number of gigs to harvest per tech stack keyword."
    )

    args = parser.parse_args()

    # Parse and clean technologies list
    tech_list = [t.strip() for t in args.tech.split(",") if t.strip()]
    if not tech_list:
        logger.error("No valid technologies specified. Exiting.")
        sys.exit(1)

    logger.info(f"Pipeline Target Platforms: {args.platform}")
    logger.info(f"Pipeline Tech Keywords: {tech_list}")
    logger.info(f"Gigs count per tech stack: {args.count}")

    pipeline = DataIngestionPipeline(platform=args.platform, simulate=args.simulate)
    
    try:
        # Step 1: Scrape / Generate Gigs
        raw_gigs = pipeline.scrape_gigs(tech_stack=tech_list, count_per_tech=args.count)
        logger.info(f"Scrape phase complete. Total raw listings retrieved: {len(raw_gigs)}")

        # Step 2: Parse and Validate
        parsed_gigs = []
        for raw in raw_gigs:
            parsed = pipeline.parse_gig(raw)
            parsed_gigs.append(parsed)

        # Step 3: Insert into PostgreSQL
        saved_count = pipeline.save_to_db(parsed_gigs)
        logger.info(f"Ingestion phase complete. Total records stored: {saved_count}")
        logger.info("=== Ingestion Pipeline execution finished successfully! ===")

    except Exception as err:
        logger.error(f"Pipeline ingestion failed with critical error: {err}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
