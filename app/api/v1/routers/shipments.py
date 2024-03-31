from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_carrier_handler, validate_user_token
from app.api.v1.schemas.schema_parcels import CarrierType
from app.schemas.schema_tracey import ShipmentStatus
from app.services.carrier.base import Carrier

from app.services.carrier.exceptions import CarrierException

router = APIRouter(
    prefix='/track',
    tags=['Track']
)


@router.get(path='/shipments', response_model=ShipmentStatus)
async def get_shipment(
        user: Annotated[str, Depends(validate_user_token)],
        carrier_type: CarrierType,
        tracking_number: str,
        carrier_handler: Annotated[Carrier, Depends(get_carrier_handler)]
):
    try:
        return await carrier_handler.get_shipment_and_transform_into_tracey()
    except CarrierException as ex:
        raise HTTPException(
            status_code=ex.status_code,
            detail=ex.message
        )
