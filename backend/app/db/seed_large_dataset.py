import sys
import os
import random
from decimal import Decimal
from typing import List, Dict, Any

# Ensure backend directory is in python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../")
    )
)

from app.core.logging import setup_logging, logger
from app.core.database import SessionLocal, engine
from app.models.market_gig import MarketGig

# Define platforms
PLATFORMS = ["Upwork", "Fiverr", "Toptal", "Freelancer"]

# Detailed tech templates and project types
TECH_PROJECT_MAP = {
    "Python": [
        "Develop web scraping pipeline with Selenium and BS4",
        "Build Machine Learning ingestion API using FastAPI",
        "Create custom Django administration portal",
        "Deploy pandas/numpy data cleaning utility",
        "Write Python script for PDF parsing and OCR processing",
        "Build automated trading bot using Python and WebSockets",
        "Develop Asyncio web crawler engine"
    ],
    "React": [
        "Create responsive Tailwind dashboard interface",
        "Build Next.js e-commerce client UI",
        "Integrate Redux state management in SPA",
        "Refactor existing React application with custom hooks",
        "Design interactive analytics charting dashboard",
        "Develop real-time Kanban project board in React"
    ],
    "Node.js": [
        "Develop Express REST API with MongoDB integration",
        "Build WebSocket real-time chat service",
        "Implement OAuth2 login with Passport.js",
        "Create serverless API handlers on AWS Lambda",
        "Optimize NestJS backend performance",
        "Build microservices API Gateway in Node.js"
    ],
    "PostgreSQL": [
        "Optimize slow SQL queries and index strategies",
        "Design multi-tenant PostgreSQL database schema",
        "Setup database replication and failover cluster",
        "Write complex PL/pgSQL stored procedures",
        "Migrate legacy database schema to PostgreSQL 15"
    ],
    "Go": [
        "Build high-concurrency gRPC microservice",
        "Develop custom CLI utility in Go",
        "Write high-throughput log processing agent",
        "Implement lightweight TCP broker",
        "Create REST API with Gin and PostgreSQL"
    ],
    "Rust": [
        "Optimize performance-critical WebAssembly module",
        "Develop systems monitoring tool in Rust",
        "Build secure cryptographic API",
        "Write custom embedded controller firmware",
        "Implement high-performance search index backend"
    ],
    "Django": [
        "Build REST API using Django REST Framework",
        "Develop multi-tenant SaaS application",
        "Integrate Celery background task processing",
        "Implement custom authentication flow in Django",
        "Configure Django CMS and caching layers"
    ],
    "Tensorflow": [
        "Train custom CNN for image classification",
        "Develop NLP pipeline using Transformer models",
        "Build recommendation engine API",
        "Optimize deep learning model weights for mobile execution",
        "Implement predictive time-series analysis engine"
    ],
    "Flutter": [
        "Build cross-platform iOS and Android mobile app",
        "Design custom UI widgets for Flutter client",
        "Integrate SQLite local caching in Flutter application",
        "Implement push notifications and map widgets",
        "Refactor state management using Riverpod/Provider"
    ],
    "Kubernetes": [
        "Design Helm charts for microservice deployments",
        "Setup Prometheus and Grafana monitoring stacks",
        "Configure Kubernetes ingress controllers and SSL",
        "Develop custom Kubernetes Operator",
        "Optimize container orchestration resource boundaries"
    ],
    "TypeScript": [
        "Convert legacy JavaScript codebase to strict TypeScript",
        "Build full-stack Next.js application with TypeScript",
        "Design type-safe API client library",
        "Implement GraphQL API schema and resolvers"
    ],
    "Docker": [
        "Containerize legacy web application and services",
        "Create multi-stage production Dockerfiles",
        "Setup Docker Compose development workflow",
        "Optimize container image size and build layers"
    ]
}

TECH_BASE_HOURLY_RATES = {
    "Python": 85.0,
    "React": 75.0,
    "Node.js": 80.0,
    "PostgreSQL": 95.0,
    "Go": 115.0,
    "Rust": 135.0,
    "Django": 90.0,
    "Tensorflow": 130.0,
    "Flutter": 70.0,
    "Kubernetes": 125.0,
    "TypeScript": 85.0,
    "Docker": 95.0
}

COMPLEXITY_MULTIPLIERS = {
    "Low": 0.85,
    "Medium": 1.0,
    "High": 1.35
}

URGENCIES = ["Low", "Medium", "High", "Urgent"]
URGENCY_MULTIPLIERS = {
    "Low": 0.95,
    "Medium": 1.0,
    "High": 1.10,
    "Urgent": 1.25
}


def generate_gig_record() -> Dict[str, Any]:
    """Generates a single realistic gig record with coherent features and target payout."""
    platform = random.choices(PLATFORMS, weights=[0.45, 0.35, 0.12, 0.08], k=1)[0]
    tech = random.choice(list(TECH_PROJECT_MAP.keys()))
    project_type = random.choice(TECH_PROJECT_MAP[tech])
    complexity = random.choices(["Low", "Medium", "High"], weights=[0.30, 0.50, 0.20], k=1)[0]
    urgency = random.choices(URGENCIES, weights=[0.20, 0.50, 0.20, 0.10], k=1)[0]

    # Auth & API presence probability based on complexity
    if complexity == "High":
        has_auth = random.random() < 0.80
        has_apis = random.random() < 0.85
    elif complexity == "Medium":
        has_auth = random.random() < 0.45
        has_apis = random.random() < 0.55
    else:  # Low
        has_auth = random.random() < 0.12
        has_apis = random.random() < 0.22

    # Estimated hours calculation
    if complexity == "Low":
        base_hours = random.uniform(5.0, 25.0)
    elif complexity == "Medium":
        base_hours = random.uniform(26.0, 80.0)
    else:  # High
        base_hours = random.uniform(81.0, 250.0)

    if has_auth:
        base_hours += random.uniform(4.0, 14.0)
    if has_apis:
        base_hours += random.uniform(5.0, 15.0)

    estimated_hours = round(base_hours, 2)

    # Hourly rate & actual payout formula
    base_rate = TECH_BASE_HOURLY_RATES[tech]
    rate_mult = COMPLEXITIES_MULT = COMPLEXITY_MULTIPLIERS[complexity]
    urgency_mult = URGENCY_MULTIPLIERS[urgency]

    # Effective rate with minor random market variation (±5%)
    market_noise = random.uniform(0.95, 1.05)
    effective_rate = base_rate * rate_mult * urgency_mult * market_noise

    payout = estimated_hours * effective_rate

    # Flat premiums for additional architectural components
    if has_auth:
        payout += random.uniform(120.0, 200.0)
    if has_apis:
        payout += random.uniform(100.0, 250.0)

    actual_payout = max(50.0, round(payout, 2))

    return {
        "platform": platform,
        "primary_tech": tech,
        "project_type": project_type,
        "complexity_level": complexity,
        "estimated_hours": Decimal(str(estimated_hours)),
        "urgency": urgency,
        "has_auth": has_auth,
        "has_third_party_apis": has_apis,
        "actual_payout": Decimal(str(actual_payout))
    }


def seed_large_dataset(total_records: int = 10000, batch_size: int = 1000) -> None:
    """Programmatically seeds total_records into market_gigs in batched transactions."""
    setup_logging()
    logger.info(f"=== Starting Seeding of {total_records:,} Records into PostgreSQL ===")

    db = SessionLocal()
    try:
        initial_count = db.query(MarketGig).count()
        logger.info(f"Initial record count in 'market_gigs': {initial_count:,}")

        inserted_total = 0
        batches = (total_records + batch_size - 1) // batch_size

        for b in range(batches):
            current_batch_size = min(batch_size, total_records - inserted_total)
            batch_objects = [
                MarketGig(**generate_gig_record()) for _ in range(current_batch_size)
            ]
            
            db.add_all(batch_objects)
            db.commit()

            inserted_total += current_batch_size
            logger.info(f"Batch {b + 1}/{batches} committed: +{current_batch_size:,} records (Total inserted: {inserted_total:,})")

        final_count = db.query(MarketGig).count()
        logger.info(f"=== Seeding Complete! Final record count in 'market_gigs': {final_count:,} ===")
    except Exception as e:
        logger.error(f"Error during large dataset seeding: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    count_to_seed = 10000
    if len(sys.argv) > 1:
        try:
            count_to_seed = int(sys.argv[1])
        except ValueError:
            pass
    seed_large_dataset(total_records=count_to_seed)
