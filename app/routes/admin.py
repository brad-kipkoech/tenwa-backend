from calendar import month_abbr
from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.quote import QuoteRequest
from app.models.shipment import Shipment, ShipmentUpdate
from app.schemas.analytics import (
    AnalyticsSummary,
    CustomerTypeMetric,
    MonthlyQuoteMetric,
    ServiceDemandMetric,
    TopDestinationMetric,
)
from app.schemas.quote import QuoteResponse, QuoteStatusUpdate
from app.schemas.shipment import ShipmentCreate, ShipmentResponse, ShipmentUpdateRequest


router = APIRouter(prefix="/api/admin", tags=["Admin"])


def quote_to_response(quote: QuoteRequest) -> QuoteResponse:
    return QuoteResponse(
        id=quote.id,
        fullName=quote.full_name,
        email=quote.email,
        phone=quote.phone,
        customerType=quote.customer_type,
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
        urgency=quote.urgency,
        contactMethod=quote.contact_method,
        notes=quote.notes,
        status=quote.status,
        createdAt=quote.created_at,
        updatedAt=quote.updated_at,
    )


def shipment_to_response(shipment: Shipment) -> ShipmentResponse:
    return ShipmentResponse(
        id=shipment.id,
        trackingCode=shipment.tracking_code,
        customerName=shipment.customer_name,
        customerPhone=shipment.customer_phone,
        serviceType=shipment.service_type,
        origin=shipment.origin,
        destination=shipment.destination,
        currentLocation=shipment.current_location,
        status=shipment.status,
        estimatedDelivery=shipment.estimated_delivery,
        remarks=shipment.remarks,
        createdAt=shipment.created_at,
        updatedAt=shipment.updated_at,
    )


def generate_tracking_code(db: Session) -> str:
    last_shipment = db.query(Shipment).order_by(Shipment.id.desc()).first()
    next_id = 1 if not last_shipment else last_shipment.id + 1
    return f"TENWA-{next_id:04d}"


def percentage_metrics(counter: Counter) -> list[ServiceDemandMetric]:
    total = sum(counter.values())

    if total == 0:
        return []

    return [
        ServiceDemandMetric(
            name=name,
            value=round((count / total) * 100),
        )
        for name, count in counter.most_common()
    ]


@router.get("/quotes", response_model=list[QuoteResponse])
def get_quotes(db: Session = Depends(get_db)):
    quotes = db.query(QuoteRequest).order_by(QuoteRequest.created_at.desc()).all()
    return [quote_to_response(quote) for quote in quotes]


@router.patch("/quotes/{quote_id}/status", response_model=QuoteResponse)
def update_quote_status(
    quote_id: int,
    payload: QuoteStatusUpdate,
    db: Session = Depends(get_db),
):
    quote = db.query(QuoteRequest).filter(QuoteRequest.id == quote_id).first()

    if not quote:
        raise HTTPException(status_code=404, detail="Quote request not found")

    quote.status = payload.status

    db.commit()
    db.refresh(quote)

    return quote_to_response(quote)


@router.get("/shipments", response_model=list[ShipmentResponse])
def get_shipments(db: Session = Depends(get_db)):
    shipments = db.query(Shipment).order_by(Shipment.created_at.desc()).all()
    return [shipment_to_response(shipment) for shipment in shipments]


@router.post(
    "/shipments",
    response_model=ShipmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_shipment(payload: ShipmentCreate, db: Session = Depends(get_db)):
    tracking_code = generate_tracking_code(db)

    shipment = Shipment(
        tracking_code=tracking_code,
        customer_name=payload.customerName,
        customer_phone=payload.customerPhone,
        service_type=payload.serviceType,
        origin=payload.origin,
        destination=payload.destination,
        current_location=payload.currentLocation,
        status=payload.status,
        estimated_delivery=payload.estimatedDelivery,
        remarks=payload.remarks,
    )

    db.add(shipment)
    db.commit()
    db.refresh(shipment)

    first_update = ShipmentUpdate(
        shipment_id=shipment.id,
        status=shipment.status,
        current_location=shipment.current_location,
        remarks=shipment.remarks,
    )

    db.add(first_update)
    db.commit()
    db.refresh(shipment)

    return shipment_to_response(shipment)


@router.patch("/shipments/{shipment_id}", response_model=ShipmentResponse)
def update_shipment(
    shipment_id: int,
    payload: ShipmentUpdateRequest,
    db: Session = Depends(get_db),
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()

    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if payload.status is not None:
        shipment.status = payload.status

    if payload.currentLocation is not None:
        shipment.current_location = payload.currentLocation

    if payload.estimatedDelivery is not None:
        shipment.estimated_delivery = payload.estimatedDelivery

    if payload.remarks is not None:
        shipment.remarks = payload.remarks

    db.commit()
    db.refresh(shipment)

    update = ShipmentUpdate(
        shipment_id=shipment.id,
        status=shipment.status,
        current_location=shipment.current_location,
        remarks=shipment.remarks,
    )

    db.add(update)
    db.commit()
    db.refresh(shipment)

    return shipment_to_response(shipment)


@router.get("/analytics/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    quotes = db.query(QuoteRequest).all()

    total_quotes = len(quotes)

    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year

    quotes_this_month = len(
        [
            quote
            for quote in quotes
            if quote.created_at
            and quote.created_at.month == current_month
            and quote.created_at.year == current_year
        ]
    )

    service_counter = Counter(quote.service_type for quote in quotes)
    customer_type_counter = Counter(quote.customer_type for quote in quotes)
    destination_counter = Counter(quote.destination for quote in quotes)

    top_service = service_counter.most_common(1)[0][0] if service_counter else "N/A"
    top_destination = (
        destination_counter.most_common(1)[0][0] if destination_counter else "N/A"
    )

    monthly_counts = {month: 0 for month in range(1, 13)}

    for quote in quotes:
        if quote.created_at and quote.created_at.year == current_year:
            monthly_counts[quote.created_at.month] += 1

    monthly_quotes = [
        MonthlyQuoteMetric(
            month=month_abbr[month],
            quotes=count,
        )
        for month, count in monthly_counts.items()
        if count > 0
    ]

    service_demand = percentage_metrics(service_counter)

    total_customer_types = sum(customer_type_counter.values())
    customer_types = []

    if total_customer_types > 0:
        customer_types = [
            CustomerTypeMetric(
                name=name,
                value=round((count / total_customer_types) * 100),
            )
            for name, count in customer_type_counter.most_common()
        ]

    top_destinations = [
        TopDestinationMetric(
            destination=destination,
            requests=count,
        )
        for destination, count in destination_counter.most_common(5)
    ]

    return AnalyticsSummary(
        totalQuotes=total_quotes,
        quotesThisMonth=quotes_this_month,
        topService=top_service,
        topDestination=top_destination,
        monthlyQuotes=monthly_quotes,
        serviceDemand=service_demand,
        customerTypes=customer_types,
        topDestinations=top_destinations,
    )