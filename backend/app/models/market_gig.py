from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, Boolean, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class MarketGig(Base):
    __tablename__ = "market_gigs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    primary_tech: Mapped[str] = mapped_column(String(100), nullable=False)
    project_type: Mapped[str] = mapped_column(String(100), nullable=False)
    complexity_level: Mapped[str] = mapped_column(String(50), nullable=False)
    estimated_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    urgency: Mapped[str] = mapped_column(String(50), nullable=False)
    has_auth: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    has_third_party_apis: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    actual_payout: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        server_default=func.now()
    )

    # Define indexes matching the schema specification
    __table_args__ = (
        Index("idx_market_gigs_tech", "primary_tech"),
    )

    def __repr__(self) -> str:
        return (
            f"<MarketGig(id={self.id}, platform='{self.platform}', tech='{self.primary_tech}', "
            f"payout={self.actual_payout})>"
        )
