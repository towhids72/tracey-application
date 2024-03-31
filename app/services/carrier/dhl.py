from logging import getLogger

import httpx

from httpx import Response
from fastapi import status

from app.schemas.schema_tracey import ShipmentStatus, ShipmentEvent, TraceyEvent
from app.services.carrier.base import Carrier
from app.services.carrier.exceptions import CarrierException
from app.utils.cache import cache

logger = getLogger(__name__)


class DHLCarrier(Carrier):
    """
    This class implements methods to retrieve shipment information
    from DHL and transform it into Tracey format.

    """

    def __init__(
            self,
            tracking_number: str,
            api_key: str,
            trace_event_map: dict
    ):
        """
        Initializes a DHLCarrier instance with the provided tracking number, API key, and trace event map.

        Args:
            tracking_number (str): The tracking number associated with the shipment.
            api_key (str): The API key required for accessing DHL services.
            trace_event_map (dict): The mapping of Tracey events.
        """
        super().__init__(
            tracking_number=tracking_number,
            trace_event_map=trace_event_map
        )
        self.api_key = api_key
        self._dhl_tracking_base_url = 'https://api-eu.dhl.com/track/shipments'
        self._cache_key = f'DHL_{self.tracking_number}'

    async def _get_shipment_tracking_info(self) -> Response:
        """
        Retrieve shipment information from the DHL API.

        Returns:
            Response from the API call.
        """

        async with httpx.AsyncClient(timeout=60) as client:
            tracking_info = await client.get(
                url=self._dhl_tracking_base_url,
                params={
                    'trackingNumber': self.tracking_number
                },
                headers={
                    'DHL-API-Key': self.api_key
                }
            )

            return tracking_info

    async def get_shipment_and_transform_into_tracey(self) -> ShipmentStatus:
        cached_shipment_info = await cache.get(self._cache_key)

        shipment_tracking_info = await self._get_shipment_tracking_info() \
            if not cached_shipment_info else cached_shipment_info

        if shipment_tracking_info.status_code == status.HTTP_404_NOT_FOUND:
            raise CarrierException(
                status_code=status.HTTP_404_NOT_FOUND,
                message='Shipment with given tracking number not found!'
            )

        if shipment_tracking_info.status_code != status.HTTP_200_OK:
            raise CarrierException(
                status_code=shipment_tracking_info.status_code,
                message=shipment_tracking_info.json()['detail']
            )

        # To prevent hitting rate limits, the result is cached for 1 hour
        # (adjustable based on the expected frequency of status changes)
        await cache.set(key=self._cache_key, value=shipment_tracking_info)

        # We have a successful response, let's transform it into Tracey
        shipment_response = shipment_tracking_info.json()

        if not shipment_response['shipments']:
            raise CarrierException(
                status_code=400,
                message=f'There is no data for the shipment with ID: {self.tracking_number}'
            )

        tracey_current_event = self._transform_shipment_event_in_tracey_event(
            shipment_event=shipment_response['shipments'][0]['status']
        ) if shipment_response['shipments'][0].get('status') else None

        shipment_events = shipment_response['shipments'][0].get('events', [])
        tracery_events = []
        for event in shipment_events:
            tracey_event = self._transform_shipment_event_in_tracey_event(event)
            if tracey_event:
                tracery_events.append(tracey_event)

        return ShipmentStatus(
            shipment_id=self.tracking_number,
            status=tracey_current_event,
            events=tracery_events
        )

    def _transform_shipment_event_in_tracey_event(
            self,
            shipment_event: dict
    ) -> ShipmentEvent | None:
        """
        Transforms a shipment event into a Tracey event.

        Args:
            shipment_event (dict): The shipment event to transform.

        Returns:
            ShipmentEvent | None: The transformed Tracey event, or None if transformation fails.
        """

        if shipment_event['description'].startswith('Processed at'):
            # Does Tracey consider all processing events as a single event?
            tracey_status = self.trace_event_map['Processed at']
        else:
            tracey_status = self.trace_event_map.get(shipment_event['description'])

        if not tracey_status:
            # If the Tracey event couldn't be found in the description key,
            # we can check whether the status code indicates delivery. It appears
            # that Tracey considers parcels collected by the recipient as delivered.
            # However, we may also classify such events as UNKNOWN.
            if shipment_event['statusCode'].title() == 'Delivered':
                tracey_status = self.trace_event_map.get('Delivered')
            else:
                logger.warning(f'Some unknown event found in the DHL API response.\n'
                               f'event: {shipment_event}')
                return None

        return ShipmentEvent(
            event_datetime=shipment_event['timestamp'],
            event=TraceyEvent(
                carrier_exception=tracey_status['carrierException'],
                exception_type=tracey_status['exceptionType'],
                is_returned=tracey_status['isReturned'],
                phase=tracey_status['phase'],
                sub_phase=tracey_status['subPhase'],
                tracey_event=tracey_status['traceyEvent'],
            )
        )
