from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Numeric, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    primary_tech: Mapped[str] = mapped_column(String(100), nullable=False)
    project_type: Mapped[str] = mapped_column(String(100), nullable=False)
    complexity_level: Mapped[str] = mapped_column(String(50), nullable=False)
    estimated_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    predicted_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    predicted_payout: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", server_default="USD")
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        server_default=func.now()
    )

    # Define indexes matching the schema specification
    __table_args__ = (
        Index("idx_prediction_logs_created", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<PredictionLog(id={self.id}, tech='{self.primary_tech}', "
            f"predicted_rate={self.predicted_rate}, currency='{self.currency}')>"
        )
