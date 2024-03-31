from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class CarrierExceptionType(Enum):
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'


class TraceyEvent(BaseModel):
    carrier_exception: str | None = None
    exception_type: CarrierExceptionType
    is_returned: bool
    phase: str
    sub_phase: str
    tracey_event: str


class ShipmentEvent(BaseModel):
    event_datetime: datetime
    event: TraceyEvent


class ShipmentStatus(BaseModel):
    shipment_id: str
    status: ShipmentEvent | None
    events: list[ShipmentEvent]
