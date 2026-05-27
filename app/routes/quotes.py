from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.quote import QuoteRequest
from app.schemas.quote import QuoteCreate, QuoteResponse
from app.services.email_service import send_quote_notification_email


router = APIRouter(prefix="/api/quotes", tags=["Quotes"])


def quote_to_response(quote: QuoteRequest) -> QuoteResponse:
    return QuoteResponse(
        id=quote.id,
        fullName=quote.full_name,
        email=quote.email,
        phone=quote.phone,
        customerType=quote.customer_type,
        requestType=quote.request_type,
        serviceType=quote.service_type,
        commodityType=quote.commodity_type,
        pieces=quote.pieces,
        weight=quote.weight,
        weightUnit=quote.weight_unit,
        origin=quote.origin,
        destination=quote.destination,
        length=quote.length,
        width=quote.width,
        height=quote.height,
        hasHsCode=quote.has_hs_code,
        hasCertificateOfConformity=quote.has_certificate_of_conformity,
        commercialValueUsd=quote.commercial_value_usd,
        urgency=quote.urgency,
        contactMethod=quote.contact_method,
        notes=quote.notes,
        status=quote.status,
        createdAt=quote.created_at,
        updatedAt=quote.updated_at,
    )


@router.post("", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
def create_quote(
    payload: QuoteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    quote = QuoteRequest(
        full_name=payload.fullName,
        email=payload.email,
        phone=payload.phone,
        customer_type=payload.customerType,
        request_type=payload.requestType,
        service_type=payload.serviceType,
        commodity_type=payload.commodityType,
        pieces=payload.pieces,
        weight=payload.weight,
        weight_unit=payload.weightUnit,
        origin=payload.origin,
        destination=payload.destination,
        length=payload.length,
        width=payload.width,
        height=payload.height,
        has_hs_code=payload.hasHsCode,
        has_certificate_of_conformity=payload.hasCertificateOfConformity,
        commercial_value_usd=payload.commercialValueUsd,
        urgency=payload.urgency,
        contact_method=payload.contactMethod,
        notes=payload.notes,
        status="New",
    )

    db.add(quote)
    db.commit()
    db.refresh(quote)

    background_tasks.add_task(send_quote_notification_email, quote)

    return quote_to_response(quote)