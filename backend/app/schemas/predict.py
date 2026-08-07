from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional


class TakeHomeBreakdownSchema(BaseModel):
    """Pydantic model structuring financial allocation breakdown metrics."""
    net_income: Decimal = Field(..., description="Net Take-Home Income (65%)")
    tax_buffer: Decimal = Field(..., description="Tax Reserve Buffer (20%)")
    tool_overheads: Decimal = Field(..., description="Software & Hardware Tool Overheads (10%)")
    non_billable_time: Decimal = Field(..., description="Non-Billable Administrative Time Buffer (5%)")


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
    currency: str = Field(default="USD", description="Target currency code (USD, EUR, GBP, LKR).", examples=["USD"])


class PredictionResponse(BaseModel):
    """Pydantic model structuring REST API prediction responses."""
    predicted_rate: Decimal = Field(..., description="Predicted equivalent hourly rate.")
    predicted_payout: Decimal = Field(..., description="Predicted total project payout.")
    currency: str = Field(default="USD", description="Currency metric used.")
    currency_symbol: str = Field(default="$", description="Currency symbol.")
    take_home_breakdown: TakeHomeBreakdownSchema = Field(..., description="Financial allocation breakdown.")
    execution_time_ms: float = Field(..., description="API execution latency in milliseconds.")
