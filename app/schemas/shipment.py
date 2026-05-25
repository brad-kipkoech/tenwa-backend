from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ShipmentCreate(BaseModel):
    customerName: str
    customerPhone: str

    serviceType: str

    origin: str
    destination: str

    currentLocation: str
    status: str

    estimatedDelivery: Optional[str] = None
    remarks: Optional[str] = None


class ShipmentUpdateRequest(BaseModel):
    status: Optional[str] = None
    currentLocation: Optional[str] = None
    estimatedDelivery: Optional[str] = None
    remarks: Optional[str] = None


class ShipmentUpdateResponse(BaseModel):
    id: int
    status: str
    currentLocation: str
    remarks: Optional[str] = None
    createdAt: datetime


class ShipmentResponse(BaseModel):
    id: int
    trackingCode: str

    customerName: str
    customerPhone: str

    serviceType: str

    origin: str
    destination: str

    currentLocation: str
    status: str

    estimatedDelivery: Optional[str] = None
    remarks: Optional[str] = None

    createdAt: datetime
    updatedAt: datetime


class PublicShipmentTrackingResponse(BaseModel):
    trackingCode: str
    customerName: str

    serviceType: str
    origin: str
    destination: str

    currentLocation: str
    status: str
    estimatedDelivery: Optional[str] = None
    remarks: Optional[str] = None

    updatedAt: datetime
    updates: List[ShipmentUpdateResponse] = []