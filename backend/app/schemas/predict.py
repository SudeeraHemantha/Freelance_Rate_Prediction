from pydantic import BaseModel, Field
from decimal import Decimal


class PredictionRequest(BaseModel):
    """Pydantic model validating incoming gig feature payloads."""
    platform: str = Field(..., description="Target freelance platform (e.g. Upwork, Fiverr).", examples=["Upwork"])
    primary_tech: str = Field(..., description="Primary technology stack (e.g. Python, React).", examples=["Python"])
    project_type: str = Field(..., description="Specific project description or title.", examples=["Machine Learning Ingestion API"])
    complexity_level: str = Field(..., description="Complexity level (Low, Medium, High).", examples=["High"])
    estimated_hours: Decimal = Field(..., gt=0, description="Estimated effort duration in hours.", examples=[40.00])
    urgency: str = Field(..., description="Urgency classification (Low, Medium, High, Urgent).", examples=["Urgent"])
    has_auth: bool = Field(default=False, description="Presence of login/authentication requirements.", examples=[True])
    has_third_party_apis: bool = Field(default=False, description="Presence of external/third-party API integrations.", examples=[True])


class PredictionResponse(BaseModel):
    """Pydantic model structuring REST API prediction responses."""
    predicted_rate: Decimal = Field(..., description="Predicted equivalent hourly rate.")
    predicted_payout: Decimal = Field(..., description="Predicted total project payout.")
    currency: str = Field(default="USD", description="Currency metric used.")
    execution_time_ms: float = Field(..., description="API execution latency in milliseconds.")
