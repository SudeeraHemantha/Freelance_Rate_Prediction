import time
import pandas as pd
from decimal import Decimal
from typing import Dict, Any
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, Depends, status

# Core imports
from app.core.logging import logger
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.limiter import limiter
from app.core.security import verify_api_key_or_token, create_access_token
from app.models.prediction_log import PredictionLog
from app.schemas.predict import PredictionRequest, PredictionResponse, TakeHomeBreakdownSchema

router = APIRouter()

CURRENCY_RATES: Dict[str, tuple[Decimal, str]] = {
    "USD": (Decimal("1.00"), "$"),
    "EUR": (Decimal("0.92"), "€"),
    "GBP": (Decimal("0.78"), "£"),
    "LKR": (Decimal("305.50"), "Rs."),
}


def log_prediction_background(payload: Dict[str, Any], predicted_rate: Decimal, predicted_payout: Decimal, currency: str, ip_address: str):
    """Background task to asynchronously record prediction metrics into PostgreSQL."""
    logger.info("Executing background logging task for rate prediction...")
    db = SessionLocal()
    try:
        log_record = PredictionLog(
            primary_tech=payload["primary_tech"],
            project_type=payload["project_type"],
            complexity_level=payload["complexity_level"],
            estimated_hours=Decimal(str(payload["estimated_hours"])),
            predicted_rate=predicted_rate,
            predicted_payout=predicted_payout,
            currency=currency,
            ip_address=ip_address
        )
        db.add(log_record)
        db.commit()
        logger.info(f"Asynchronous prediction logging completed. Log ID: {log_record.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save prediction log: {e}", exc_info=True)
    finally:
        db.close()


@router.post("/token", status_code=status.HTTP_200_OK)
async def get_demo_token():
    """Generates a valid enterprise JWT bearer token for testing/authentication."""
    token = create_access_token(data={"sub": "enterprise_user_1", "role": "admin"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600,
        "demo_api_key": settings.API_KEY
    }


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
@limiter.limit(settings.RATE_LIMIT_PER_MINUTE)
async def predict_rate(
    request: Request,
    payload: PredictionRequest, 
    background_tasks: BackgroundTasks,
    auth_data: Dict[str, Any] = Depends(verify_api_key_or_token)
):
    """Calculates live freelance pricing forecasts using the trained LightGBM model pipeline."""
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"

    logger.info(
        "Received prediction request",
        client_ip=client_ip,
        auth_type=auth_data.get("auth_type"),
        tech=payload.primary_tech,
        hours=float(payload.estimated_hours),
        currency=payload.currency
    )

    # 1. Fetch the loaded pipeline model from application state
    model_pipeline = getattr(request.app.state, "rate_predictor", None)
    if model_pipeline is None:
        logger.error("Machine learning pipeline model is not loaded in application state.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Machine learning model is currently unavailable/not loaded."
        )

    try:
        # 2. Convert incoming request payload into a Pandas DataFrame conforming to ML features
        input_data = pd.DataFrame([{
            "platform": payload.platform,
            "primary_tech": payload.primary_tech,
            "project_type": payload.project_type,
            "complexity_level": payload.complexity_level,
            "urgency": payload.urgency,
            "estimated_hours": float(payload.estimated_hours),
            "has_auth": int(payload.has_auth),
            "has_third_party_apis": int(payload.has_third_party_apis)
        }])

        # 3. Predict total payout in USD
        predicted_payout_usd = float(model_pipeline.predict(input_data)[0])
        
        # Guard payouts below zero (bounds constraint)
        if predicted_payout_usd < 0.0:
            predicted_payout_usd = 50.00

        # 4. Process Multi-Currency Conversion
        target_currency = payload.currency.upper() if payload.currency else "USD"
        multiplier, currency_symbol = CURRENCY_RATES.get(target_currency, (Decimal("1.00"), "$"))

        converted_payout_float = predicted_payout_usd * float(multiplier)
        estimated_hours_float = float(payload.estimated_hours)
        converted_rate_float = converted_payout_float / estimated_hours_float

        # Format numeric conversions to Decimal with 2 decimal places precision
        predicted_payout_dec = Decimal(f"{converted_payout_float:.2f}")
        predicted_rate_dec = Decimal(f"{converted_rate_float:.2f}")

        # 5. Compute Financial Breakdown Metrics (65% Net, 20% Tax, 10% Tools, 5% Admin)
        take_home_breakdown = TakeHomeBreakdownSchema(
            net_income=Decimal(f"{(converted_payout_float * 0.65):.2f}"),
            tax_buffer=Decimal(f"{(converted_payout_float * 0.20):.2f}"),
            tool_overheads=Decimal(f"{(converted_payout_float * 0.10):.2f}"),
            non_billable_time=Decimal(f"{(converted_payout_float * 0.05):.2f}")
        )

        # Measure latency
        execution_time_ms = (time.time() - start_time) * 1000

        # 6. Delegate asynchronous database logging to FastAPI background workers
        background_tasks.add_task(
            log_prediction_background, 
            payload.model_dump() if hasattr(payload, "model_dump") else payload.dict(), 
            predicted_rate_dec, 
            predicted_payout_dec,
            target_currency,
            client_ip
        )

        return PredictionResponse(
            predicted_rate=predicted_rate_dec,
            predicted_payout=predicted_payout_dec,
            currency=target_currency,
            currency_symbol=currency_symbol,
            take_home_breakdown=take_home_breakdown,
            execution_time_ms=execution_time_ms
        )

    except Exception as err:
        logger.error(f"Inference prediction failed with error: {err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failed: {str(err)}"
        )
