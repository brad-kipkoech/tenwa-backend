from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.sql import func

from app.database import Base


class QuoteRequest(Base):
    __tablename__ = "quote_requests"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, index=True)
    phone = Column(String(50), nullable=False)

    customer_type = Column(String(80), nullable=False)

    # This separates normal quote requests from import requests.
    # general = normal quote request, import = import request
    request_type = Column(String(80), nullable=False, default="general")

    service_type = Column(String(120), nullable=False)
    commodity_type = Column(String(120), nullable=False)

    pieces = Column(Integer, nullable=False, default=1)
    weight = Column(Integer, nullable=False, default=1)
    weight_unit = Column(String(20), nullable=False, default="kg")

    origin = Column(String(150), nullable=False)
    destination = Column(String(150), nullable=False)

    length = Column(String(50), nullable=True)
    width = Column(String(50), nullable=True)
    height = Column(String(50), nullable=True)

    # Import-specific fields
    has_hs_code = Column(String(20), nullable=True)
    has_certificate_of_conformity = Column(String(20), nullable=True)
    commercial_value_usd = Column(Numeric(12, 2), nullable=True)

    urgency = Column(String(80), nullable=False, default="Normal")
    contact_method = Column(String(80), nullable=False, default="Phone")
    notes = Column(Text, nullable=True)

    status = Column(String(80), nullable=False, default="New")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )