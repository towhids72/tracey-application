import pytest
from httpx import AsyncClient
from fastapi import status

from tests.conftest import async_client


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get('/health')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == 'ok'
