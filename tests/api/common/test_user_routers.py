import pytest
from httpx import AsyncClient
from fastapi import status

from app.schemas.schema_users import User, UserInDB, Token
from tests.conftest import async_client, user_schema_instance


@pytest.mark.asyncio
async def test_user_create(async_client: AsyncClient, user_schema_instance: UserInDB):
    response = await async_client.post(
        url='/user/register',
        json=user_schema_instance.model_dump()
    )

    assert response.status_code == status.HTTP_200_OK
    user = User(**response.json())
    assert isinstance(user, User)
    assert user.username == user_schema_instance.username
    assert user.email == user_schema_instance.email


@pytest.mark.asyncio
async def test_get_token_valid_credentials(async_client: AsyncClient, user_schema_instance: UserInDB):
    response = await async_client.post(
        url='/user/register',
        json=user_schema_instance.model_dump()
    )

    assert response.status_code == status.HTTP_200_OK

    response = await async_client.post(
        url='/user/token',
        data={
            'username': user_schema_instance.username,
            'password': user_schema_instance.password
        }
    )

    assert response.status_code == status.HTTP_200_OK

    token = Token(**response.json())
    assert isinstance(token, Token)


@pytest.mark.asyncio
async def test_get_token_invalid_credentials(async_client: AsyncClient, user_schema_instance: UserInDB):
    response = await async_client.post(
        url='/user/token',
        data={
            'username': 'SomeInvalidUsername',
            'password': 'InvalidPassword'
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == 'Invalid authentication credentials'
