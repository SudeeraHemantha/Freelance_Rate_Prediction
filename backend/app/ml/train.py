import sys
import os
import numpy as np
import pandas as pd
from decimal import Decimal
from typing import Tuple

# Add backend directory to python path dynamically
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../")
    )
)

# Core imports
from app.core.logging import setup_logging, logger
from app.core.database import engine

# ML imports
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
from lightgbm import LGBMRegressor
import joblib

# Optional MLflow import
try:
    import mlflow
    import mlflow.sklearn
except ImportError:
    mlflow = None


def load_data_from_db() -> pd.DataFrame:
    """Fetches historical freelance gigs from the database and loads them into a pandas DataFrame."""
    logger.info("Connecting to PostgreSQL and pulling historical market gigs...")
    
    # We load directly from PostgreSQL using the SQLAlchemy engine
    query = "SELECT * FROM market_gigs"
    df = pd.read_sql_query(query, con=engine)
    logger.info(f"Successfully loaded {len(df)} records from 'market_gigs' table.")
    return df


def preprocess_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Cleans columns, coerces types, and splits feature variables from target variables."""
    # Create copy to avoid SettingWithCopy warnings
    data = df.copy()

    # Coerce Decimal types (from PostgreSQL Numeric) to Float for sklearn/lightgbm
    decimal_cols = ["estimated_hours", "actual_payout"]
    for col in decimal_cols:
        if col in data.columns:
            data[col] = data[col].apply(lambda x: float(x) if isinstance(x, (Decimal, float, int, str)) else 0.0)

    # Boolean columns mapping
    bool_cols = ["has_auth", "has_third_party_apis"]
    for col in bool_cols:
        if col in data.columns:
            data[col] = data[col].astype(int)

    # Validate target column exists
    if "actual_payout" not in data.columns:
        raise ValueError("Target column 'actual_payout' is missing from the dataset.")

    # Features and target split
    categorical_features = ["platform", "primary_tech", "project_type", "complexity_level", "urgency"]
    numeric_features = ["estimated_hours"]
    passthrough_features = ["has_auth", "has_third_party_apis"]

    feature_cols = categorical_features + numeric_features + passthrough_features
    X = data[feature_cols]
    y = data["actual_payout"]

    logger.info(f"Features parsed successfully. Shape: {X.shape}")
    return X, y


def train_model() -> Tuple[Pipeline, float, float]:
    """Orchestrates features engineering, model training, evaluation, and logging."""
    setup_logging()
    logger.info("=== Starting Machine Learning Training Engine ===")

    # 1. Load data
    df = load_data_from_db()
    if len(df) < 10:
        logger.error("Dataset too small to train LightGBM Regressor. Ingest more data and retry.")
        raise ValueError("Insufficient data points in PostgreSQL database.")

    # 2. Preprocess
    X, y = preprocess_data(df)

    # 3. Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    logger.info(f"Split completed. Training set: {X_train.shape[0]} samples, Testing set: {X_test.shape[0]} samples.")

    # 4. Pipeline Construction
    # Categorical features list
    categorical_features = ["platform", "primary_tech", "project_type", "complexity_level", "urgency"]
    numeric_features = ["estimated_hours"]
    passthrough_features = ["has_auth", "has_third_party_apis"]

    # Preprocessing transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ("num", StandardScaler(), numeric_features),
            ("pass", "passthrough", passthrough_features)
        ]
    )

    # Define LGBM Regressor hyperparameters
    lgbm_params = {
        "n_estimators": 100,
        "learning_rate": 0.05,
        "num_leaves": 31,
        "random_state": 42,
        "verbosity": -1  # Silence internal lightgbm warnings
    }

    # Combined model pipeline
    model_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", LGBMRegressor(**lgbm_params))
        ]
    )

    # 5. Model Fitting & Optional MLflow Tracking
    logger.info("Fitting LightGBM model pipeline on training dataset...")
    if mlflow is not None:
        try:
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../mlflow.db")).replace("\\", "/")
            mlflow.set_tracking_uri(f"sqlite:///{db_path}")
            mlflow.set_experiment("Freelance_Rate_Regressor")
            with mlflow.start_run() as run:
                model_pipeline.fit(X_train, y_train)
                mlflow.log_params(lgbm_params)
                mlflow.log_param("test_size", 0.2)
                mlflow.log_param("total_samples", len(df))
                y_pred = model_pipeline.predict(X_test)
                rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
                r2 = float(r2_score(y_test, y_pred))
                mlflow.log_metric("rmse", rmse)
                mlflow.log_metric("r2_score", r2)
                mlflow.sklearn.log_model(model_pipeline, "model_pipeline", serialization_format="pickle")
                logger.info(f"MLflow Run completed. ID: {run.info.run_id}")
        except Exception as mlf_err:
            logger.warning(f"MLflow logging skipped: {mlf_err}")
            model_pipeline.fit(X_train, y_train)
            y_pred = model_pipeline.predict(X_test)
            rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
            r2 = float(r2_score(y_test, y_pred))
    else:
        model_pipeline.fit(X_train, y_train)
        y_pred = model_pipeline.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = float(r2_score(y_test, y_pred))

    logger.info(f"Evaluation Metrics: RMSE = {rmse:.4f}, R2 = {r2:.4f}")

    # 6. Local Serialization
    # Resolve local directory paths
    ml_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(ml_dir, "models")
    os.makedirs(models_dir, exist_ok=True)

    model_path = os.path.join(models_dir, "rate_predictor_model.joblib")
    logger.info(f"Serializing trained model pipeline to local file: {model_path}")
    joblib.dump(model_pipeline, model_path)

    # Verify reload
    try:
        loaded = joblib.load(model_path)
        test_pred = loaded.predict(X_test.iloc[[0]])
        logger.info(f"Local model load verification successful. Sample prediction: {test_pred[0]:.2f}")
    except Exception as e:
        logger.error(f"Failed to verify local model serialization: {e}")
        raise

    logger.info("=== Machine Learning Ingestion & Training complete! ===")
    return model_pipeline, rmse, r2


if __name__ == "__main__":
    try:
        train_model()
    except Exception as err:
        logger.error(f"ML training script failed: {err}", exc_info=True)
        sys.exit(1)
