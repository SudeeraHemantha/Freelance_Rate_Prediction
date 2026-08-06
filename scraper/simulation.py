import random
from typing import Dict, Any, List
from decimal import Decimal

# Configure logging
import logging
logger = logging.getLogger("scraper.simulation")

# Predefined templates for realistic gig generation
TECH_TEMPLATES = {
    "Python": [
        "Develop web scraping pipeline with Selenium and BS4",
        "Build Machine Learning ingestion API using FastAPI",
        "Create custom Django administration portal",
        "Deploy pandas/numpy data cleaning utility",
        "Write Python script for PDF parsing and OCR processing"
    ],
    "React": [
        "Create responsive Tailwind dashboard interface",
        "Build Next.js e-commerce client UI",
        "Integrate Redux state management in SPA",
        "Refactor existing React application with custom hooks",
        "Design interactive analytics charting dashboard"
    ],
    "Node.js": [
        "Develop Express REST API with MongoDB integration",
        "Build WebSocket real-time chat service",
        "Implement OAuth2 login with Passport.js",
        "Create serverless API handlers on AWS Lambda",
        "Optimize NestJS backend performance"
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
    ]
}

GENERIC_TEMPLATES = [
    "Develop freelance backend API for mobile integration",
    "Build custom landing page and responsive layout",
    "Fix database latency and refactor queries",
    "Setup CI/CD deployment pipeline for web application",
    "Implement third-party API integration and payments"
]

PLATFORMS = ["Upwork", "Fiverr"]
COMPLEXITIES = ["Low", "Medium", "High"]
URGENCIES = ["Low", "Medium", "High", "Urgent"]


def generate_simulated_gig(platform: str = None, tech_stack: str = None) -> Dict[str, Any]:
    """Generates a high-fidelity simulated freelance job listing with coherent metrics."""
    # Select Platform
    if not platform or platform.capitalize() not in PLATFORMS:
        platform = random.choices(PLATFORMS, weights=[0.6, 0.4], k=1)[0]
    else:
        platform = platform.capitalize()

    # Select Tech Stack
    if not tech_stack:
        tech = random.choice(list(TECH_TEMPLATES.keys()))
    else:
        tech = tech_stack.strip().capitalize()

    # Select Project Type (Title)
    templates = TECH_TEMPLATES.get(tech, GENERIC_TEMPLATES)
    project_type = random.choice(templates)

    # Complexity distribution: Low (25%), Medium (50%), High (25%)
    complexity = random.choices(COMPLEXITIES, weights=[0.25, 0.50, 0.25], k=1)[0]

    # Urgency distribution: Low (15%), Medium (50%), High (25%), Urgent (10%)
    urgency = random.choices(URGENCIES, weights=[0.15, 0.50, 0.25, 0.10], k=1)[0]

    # Authentication & API presence (conditioned on complexity)
    if complexity == "High":
        has_auth = random.random() < 0.75
        has_apis = random.random() < 0.85
    elif complexity == "Medium":
        has_auth = random.random() < 0.40
        has_apis = random.random() < 0.50
    else:  # Low
        has_auth = random.random() < 0.10
        has_apis = random.random() < 0.20

    # Estimated Hours (conditioned on complexity and features)
    if complexity == "Low":
        base_hours = random.randint(5, 20)
    elif complexity == "Medium":
        base_hours = random.randint(21, 75)
    else:  # High
        base_hours = random.randint(76, 220)

    # Add extra hours for features
    if has_auth:
        base_hours += random.randint(5, 15)
    if has_apis:
        base_hours += random.randint(4, 12)

    estimated_hours = Decimal(base_hours).quantize(Decimal("0.01"))

    # Hourly rates based on tech stack
    tech_base_rates = {
        "Python": 85,
        "Django": 90,
        "Tensorflow": 125,
        "React": 75,
        "Node.js": 80,
        "Go": 115,
        "Rust": 135,
        "Kubernetes": 130,
        "Flutter": 70
    }
    base_rate = tech_base_rates.get(tech, 65)

    # Rate adjustments based on complexity
    complexity_multipliers = {
        "Low": 0.8,
        "Medium": 1.0,
        "High": 1.3
    }
    rate_multiplier = complexity_multipliers[complexity]
    
    # Calculate payout
    hourly_rate = Decimal(base_rate) * Decimal(rate_multiplier)
    payout = (estimated_hours * hourly_rate).quantize(Decimal("0.01"))

    # Add flat fee premiums for features
    if has_auth:
        payout += Decimal("150.00")
    if has_apis:
        payout += Decimal("100.00")

    # Urgent premium (15% increase)
    if urgency == "Urgent":
        payout *= Decimal("1.15")

    # Round actual payout to 2 decimal places
    actual_payout = payout.quantize(Decimal("0.01"))

    # Clamp payouts
    if actual_payout < Decimal("20.00"):
        actual_payout = Decimal("50.00")

    return {
        "platform": platform,
        "primary_tech": tech,
        "project_type": project_type,
        "complexity_level": complexity,
        "estimated_hours": estimated_hours,
        "urgency": urgency,
        "has_auth": has_auth,
        "has_third_party_apis": has_apis,
        "actual_payout": actual_payout
    }


def generate_simulated_gigs_batch(count: int, platform: str = None, tech_stack: List[str] = None) -> List[Dict[str, Any]]:
    """Generates a list of multiple simulated freelance jobs."""
    gigs = []
    for _ in range(count):
        tech = random.choice(tech_stack) if tech_stack else None
        gig = generate_simulated_gig(platform=platform, tech_stack=tech)
        gigs.append(gig)
    return gigs
