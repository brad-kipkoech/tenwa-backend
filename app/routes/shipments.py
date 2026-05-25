from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.shipment import Shipment
from app.schemas.shipment import (
    PublicShipmentTrackingResponse,
    ShipmentUpdateResponse,
)


router = APIRouter(prefix="/api/shipments", tags=["Shipments"])


def shipment_update_to_response(update) -> ShipmentUpdateResponse:
    return ShipmentUpdateResponse(
        id=update.id,
        status=update.status,
        currentLocation=update.current_location,
        remarks=update.remarks,
        createdAt=update.created_at,
    )


@router.get("/track/{tracking_code}", response_model=PublicShipmentTrackingResponse)
def track_shipment(tracking_code: str, db: Session = Depends(get_db)):
    shipment = (
        db.query(Shipment)
        .options(joinedload(Shipment.updates))
        .filter(Shipment.tracking_code == tracking_code.upper())
        .first()
    )

    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    sorted_updates = sorted(
        shipment.updates,
        key=lambda update: update.created_at,
        reverse=True,
    )

    return PublicShipmentTrackingResponse(
        trackingCode=shipment.tracking_code,
        customerName=shipment.customer_name,
        serviceType=shipment.service_type,
        origin=shipment.origin,
        destination=shipment.destination,
        currentLocation=shipment.current_location,
        status=shipment.status,
        estimatedDelivery=shipment.estimated_delivery,
        remarks=shipment.remarks,
        updatedAt=shipment.updated_at,
        updates=[shipment_update_to_response(update) for update in sorted_updates],
    )