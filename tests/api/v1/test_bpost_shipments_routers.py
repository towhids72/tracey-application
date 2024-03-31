import pytest
from httpx import AsyncClient
from fastapi import status

from app.api.v1.schemas.schema_parcels import CarrierType
from tests.conftest import async_client


@pytest.mark.asyncio
async def test_valid_shipment_transform_to_tracey(async_client: AsyncClient, access_token: str):
    with pytest.raises(NotImplementedError):
        response = await async_client.get(
            url='/v1/track/shipments',
            params={
                'carrier_type': CarrierType.BPOST.value,
                'tracking_number': 'JVGL06252498000966068673'
            },
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
