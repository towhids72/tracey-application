import pytest
from httpx import AsyncClient
from fastapi import status

from app.api.v1.schemas.schema_parcels import CarrierType
from app.schemas.schema_tracey import ShipmentStatus
from tests.conftest import async_client


@pytest.mark.asyncio
async def test_valid_shipment_transform_to_tracey(async_client: AsyncClient, access_token: str):
    response = await async_client.get(
        url='/v1/track/shipments',
        params={
            'carrier_type': CarrierType.DHL.value,
            'tracking_number': 'JVGL06252498000966068673'
        },
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == status.HTTP_200_OK
    transformed_shipment = ShipmentStatus(**response.json())
    assert isinstance(transformed_shipment, ShipmentStatus)


@pytest.mark.asyncio
async def test_invalid_shipment_transform_to_tracey(async_client: AsyncClient, access_token: str):
    response = await async_client.get(
        url='/v1/track/shipments',
        params={
            'carrier_type': CarrierType.DHL.value,
            'tracking_number': 'SomeInvalidShipmentID'
        },
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Shipment with given tracking number not found!'


@pytest.mark.asyncio
async def test_unauthorized_shipment_transform_request(async_client: AsyncClient):
    response = await async_client.get(
        url='/v1/track/shipments',
        params={
            'carrier_type': CarrierType.DHL.value,
            'tracking_number': 'JVGL06252498000966068673'
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == 'Not authenticated'
