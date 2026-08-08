import os
import sys
import time
import joblib
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add backend directory to python path dynamically
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../")
    )
)

# Core imports
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import SessionLocal, get_db
from app.core.limiter import limiter
from app.api.v1 import predict_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application lifecycle: provisions database schemas, loads ML model into memory, cleans up on exit."""
    setup_logging()
    logger.info("=== Initializing FastAPI Server Lifespan Lifecycle ===")
    
    # 0. Ensure DB tables are created (retry loop during initial container startup)
    for attempt in range(1, 11):
        try:
            from app.core.database import engine, Base
            from app.models import MarketGig, PredictionLog
            Base.metadata.create_all(bind=engine)
            logger.info("Database schema verified and tables created successfully.")
            break
        except Exception as err:
            logger.warning(f"Database connection attempt {attempt}/10 failed: {err}. Retrying in 2s...")
            time.sleep(2)
    
    # 1. Resolve local path of serialized joblib model
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "ml", "models", "rate_predictor_model.joblib")
    
    logger.info(f"Loading trained LightGBM model pipeline from: {model_path}")
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at path: {model_path}")
        
        # Load the model directly into application state
        app.state.rate_predictor = joblib.load(model_path)
        logger.info("Machine learning model pipeline loaded successfully into application state.")
    except Exception as e:
        logger.warning(f"Could not load pre-serialized model file ({e}). Automatically training model from Neon database...")
        try:
            from app.ml.train import train_model
            model_pipeline, rmse, r2 = train_model()
            app.state.rate_predictor = model_pipeline
            logger.info(f"Machine learning model pipeline trained and loaded successfully into application state (R²: {r2:.4f}).")
        except Exception as train_err:
            logger.error(f"Failed to auto-train ML model artifact during server startup: {train_err}", exc_info=True)
            app.state.rate_predictor = None

    yield

    # 2. Cleanup operations during shutdown
    logger.info("Clearing preloaded models from application state...")
    if hasattr(app.state, "rate_predictor"):
        del app.state.rate_predictor
    logger.info("=== FastAPI Server Lifespan Lifecycle terminated ===")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Production-grade serving API for the Freelance Rate & Demand Predictor LightGBM model.",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Attach slowapi rate limiter state and rate limit exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS Middleware
cors_origins_list = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list if cors_origins_list else ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.middleware("http")
async def log_request_lifecycle(request: Request, call_next):
    """Observability Middleware: Records HTTP request lifecycle metrics, latency, and client IPs using structlog."""
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        response = await call_next(request)
        process_time_ms = round((time.time() - start_time) * 1000, 2)
        
        logger.info(
            "HTTP Request Completed",
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
            status_code=response.status_code,
            latency_ms=process_time_ms
        )
        return response
    except Exception as exc:
        process_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(
            "Unhandled HTTP Request Error",
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
            error=str(exc),
            latency_ms=process_time_ms,
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unhandled internal server error occurred."}
        )


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """API health diagnostic route. Returns status of model loading and PostgreSQL connectivity."""
    db_healthy = False
    db_detail = "Healthy"
    
    # 1. Test database connection
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception as e:
        db_detail = f"PostgreSQL connection failed: {str(e)}"
        logger.error(db_detail)

    # 2. Check ML model state
    model_loaded = getattr(app.state, "rate_predictor", None) is not None
    model_detail = "Model is loaded and ready." if model_loaded else "Model artifact is not loaded or failed to load."

    overall_status = "healthy" if (db_healthy and model_loaded) else "degraded"
    
    response_payload = {
        "status": overall_status,
        "environment": settings.ENV,
        "services": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "message": db_detail
            },
            "ml_model": {
                "status": "healthy" if model_loaded else "unhealthy",
                "message": model_detail
            }
        }
    }

    if overall_status == "degraded":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response_payload
        )

    return response_payload


# Include v1 API Routers
app.include_router(predict_router, prefix="/api/v1", tags=["prediction"])


@app.get("/")
def read_root():
    """Default root endpoint pointing users to Swagger documentation."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "documentation": "/docs"
    }
