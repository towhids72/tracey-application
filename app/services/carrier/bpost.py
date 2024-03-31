from app.schemas.schema_tracey import ShipmentStatus
from app.services.carrier.base import Carrier


class BPostCarrier(Carrier):
    """
    This class implements methods to retrieve shipment information
    from BPOST and transform it into Tracey format.
    """

    def __init__(
            self,
            tracking_number: str,
            trace_event_map: dict
    ):
        super().__init__(
            tracking_number=tracking_number,
            trace_event_map=trace_event_map
        )

    async def get_shipment_and_transform_into_tracey(self) -> ShipmentStatus:
        raise NotImplementedError
