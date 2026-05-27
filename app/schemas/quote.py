from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr


class QuoteCreate(BaseModel):
    fullName: str
    email: EmailStr
    phone: str

    customerType: str

    # general = normal quote request
    # import = import request
    requestType: str = "general"

    serviceType: str
    commodityType: str

    pieces: int = 1
    weight: int = 1
    weightUnit: str = "kg"

    origin: str
    destination: str

    length: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None

    # Import-specific fields
    hasHsCode: Optional[str] = None
    hasCertificateOfConformity: Optional[str] = None
    commercialValueUsd: Optional[Decimal] = None

    urgency: str = "Normal"
    contactMethod: str = "Phone"
    notes: Optional[str] = None


class QuoteStatusUpdate(BaseModel):
    status: str


class QuoteResponse(BaseModel):
    id: int

    fullName: str
    email: str
    phone: str

    customerType: str
    requestType: str

    serviceType: str
    commodityType: str

    pieces: int
    weight: int
    weightUnit: str

    origin: str
    destination: str

    length: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None

    # Import-specific fields
    hasHsCode: Optional[str] = None
    hasCertificateOfConformity: Optional[str] = None
    commercialValueUsd: Optional[Decimal] = None

    urgency: str
    contactMethod: str
    notes: Optional[str] = None

    status: str
    createdAt: datetime
    updatedAt: datetime