from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)

    tracking_code = Column(String(80), unique=True, nullable=False, index=True)

    customer_name = Column(String(150), nullable=False)
    customer_phone = Column(String(50), nullable=False)

    service_type = Column(String(120), nullable=False)

    origin = Column(String(150), nullable=False)
    destination = Column(String(150), nullable=False)

    current_location = Column(String(150), nullable=False)
    status = Column(String(120), nullable=False)

    estimated_delivery = Column(String(80), nullable=True)
    remarks = Column(Text, nullable=True)

    updates = relationship(
        "ShipmentUpdate",
        back_populates="shipment",
        cascade="all, delete-orphan",
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class ShipmentUpdate(Base):
    __tablename__ = "shipment_updates"

    id = Column(Integer, primary_key=True, index=True)

    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)

    status = Column(String(120), nullable=False)
    current_location = Column(String(150), nullable=False)
    remarks = Column(Text, nullable=True)

    shipment = relationship("Shipment", back_populates="updates")

    created_at = Column(DateTime(timezone=True), server_default=func.now())