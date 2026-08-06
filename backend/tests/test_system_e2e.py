import sys
import os
import requests
import json

# Ensure backend directory is in python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../")
    )
)

from app.core.logging import setup_logging, logger
from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.models.market_gig import MarketGig


def run_system_e2e_tests():
    """Runs comprehensive end-to-end integration tests for the enterprise stack."""
    setup_logging()
    logger.info("=== Starting End-to-End Enterprise System Verification Suite ===")

    # 1. PostgreSQL Database & Ingestion Assertion
    logger.info("Test 1: Verifying PostgreSQL market_gigs dataset...")
    db = SessionLocal()
    try:
        count = db.query(MarketGig).count()
        logger.info(f"PostgreSQL MarketGig table record count: {count:,}")
        assert count >= 10000, f"Expected at least 10,000 records, found {count}"
        logger.info("Test 1 PASSED: Database dataset scale verified.")
    finally:
        db.close()

    # 2. FastAPI Health Endpoint Check
    logger.info("Test 2: Verifying FastAPI backend /health endpoint...")
    backend_url = "http://localhost:8000"
    health_resp = requests.get(f"{backend_url}/health", timeout=5)
    assert health_resp.status_code == 200, f"Health check failed with status {health_resp.status_code}"
    health_data = health_resp.json()
    assert health_data["status"] == "healthy", f"Health status degraded: {health_data}"
    logger.info(f"Test 2 PASSED: Backend status: {health_data['status']}")

    # 3. Security Guard (Unauthenticated Request)
    logger.info("Test 3: Verifying Security Guard (Unauthenticated Access Blocking)...")
    payload = {
        "platform": "Upwork",
        "primary_tech": "Python",
        "project_type": "Machine Learning API",
        "complexity_level": "High",
        "estimated_hours": 40,
        "urgency": "Urgent",
        "has_auth": True,
        "has_third_party_apis": True
    }
    unauth_resp = requests.post(f"{backend_url}/api/v1/predict", json=payload, timeout=5)
    assert unauth_resp.status_code == 401, f"Expected 401 Unauthorized, got {unauth_resp.status_code}"
    logger.info("Test 3 PASSED: Unauthenticated request correctly blocked with HTTP 401.")

    # 4. Security Authentication via X-API-Key
    logger.info("Test 4: Verifying Authenticated Prediction via API Key...")
    headers = {"X-API-Key": settings.API_KEY}
    auth_resp = requests.post(f"{backend_url}/api/v1/predict", json=payload, headers=headers, timeout=5)
    assert auth_resp.status_code == 200, f"Authenticated prediction failed with status {auth_resp.status_code}: {auth_resp.text}"
    pred_data = auth_resp.json()
    assert "predicted_rate" in pred_data and "predicted_payout" in pred_data
    logger.info(f"Test 4 PASSED: Predicted Rate = ${pred_data['predicted_rate']}/hr, Payout = ${pred_data['predicted_payout']}")

    # 5. JWT Bearer Token Flow
    logger.info("Test 5: Verifying JWT Bearer Token Generation & Authentication...")
    token_resp = requests.post(f"{backend_url}/api/v1/token", timeout=5)
    assert token_resp.status_code == 200, f"Token issuance failed with status {token_resp.status_code}"
    jwt_token = token_resp.json()["access_token"]
    
    jwt_headers = {"Authorization": f"Bearer {jwt_token}"}
    jwt_auth_resp = requests.post(f"{backend_url}/api/v1/predict", json=payload, headers=jwt_headers, timeout=5)
    assert jwt_auth_resp.status_code == 200, f"JWT authenticated prediction failed: {jwt_auth_resp.text}"
    logger.info("Test 5 PASSED: JWT Bearer Token authenticated successfully.")

    # 6. Next.js Frontend Dashboard Verification
    logger.info("Test 6: Verifying Next.js Production Dashboard Interface...")
    frontend_url = "http://localhost:3000"
    fe_resp = requests.get(frontend_url, timeout=5)
    assert fe_resp.status_code == 200, f"Frontend check failed with status {fe_resp.status_code}"
    logger.info("Test 6 PASSED: Next.js Frontend Dashboard active at http://localhost:3000.")

    logger.info("=== All 6 End-to-End Enterprise System Tests PASSED Successfully! ===")


if __name__ == "__main__":
    try:
        run_system_e2e_tests()
    except Exception as err:
        logger.error(f"E2E Test Suite Failure: {err}", exc_info=True)
        sys.exit(1)
