import abc

from app.schemas.schema_tracey import ShipmentStatus


class Carrier(abc.ABC):
    """
    This is the base class for carriers.

    All carriers should extend this class and implement all abstract methods.
    """

    def __init__(
            self,
            tracking_number: str,
            trace_event_map: dict
    ):
        self.tracking_number = tracking_number
        self.trace_event_map = trace_event_map

    @abc.abstractmethod
    async def get_shipment_and_transform_into_tracey(self) -> ShipmentStatus:
        """
        Retrieves shipment information and transforms it into Tracey format.

        Returns:
            ShipmentStatus: The shipment status in Tracey format.

        Raises:
            CarrierException: If there are errors in retrieving or transforming shipment information.
        """
        raise NotImplementedError
