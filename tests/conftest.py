from datetime import timedelta
from typing import Callable, Generator, AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.auth.users import UserAuthServices
from app.config.base import Settings
from app.db.database import DatabaseHandler
from app.db.models import UserModel
from app.schemas.schema_users import UserInDB


def get_test_db_handler():
    """
    Retrieves the database credentials from the settings and initializes a DatabaseHandler instance.

    Returns:
        DatabaseHandler: An instance of DatabaseHandler.
    """
    settings = Settings()
    return DatabaseHandler(
        database='test_tracey_db',
        db_username=settings.POSTGRES_USERNAME,
        db_password=settings.POSTGRES_PASSWORD,
        db_host=settings.POSTGRES_HOST,
        db_port=int(settings.POSTGRES_PORT),
    )


@pytest.fixture
def override_get_database_dependency() -> Callable:
    """
    A pytest fixture to override the database handler dependency for testing.
    """

    def _override_get_database_dependency():
        db_handler = get_test_db_handler()
        db_handler.initialize()
        return db_handler.create_session()

    return _override_get_database_dependency


@pytest.fixture
def postgres() -> Generator[DatabaseHandler, None, None]:
    """
    Fixture to set up and tear down a PostgreSQL database for testing.

    Yields:
        DatabaseHandler: An instance of the database handler for testing.
    """
    db_handler = get_test_db_handler()
    db_handler.initialize()
    yield db_handler

    # Perform cleanup after all tests are done
    db_handler.drop_tables()
    db_handler.engine.dispose()


@pytest.fixture
def user_model_instance() -> UserModel:
    return UserModel(
        email='john.doe@example.com',
        username='johndoe',
        password='somesecret123'
    )


@pytest.fixture
def user_schema_instance() -> UserInDB:
    return UserInDB(
        username='johndoe',
        email='john.doe@example.com',
        password='somesecret123'
    )


@pytest_asyncio.fixture
async def app(
        override_get_database_dependency: Callable,
) -> AsyncGenerator[FastAPI, None]:
    """
    Creates a FastAPI test app with overridden database dependencies.

    Args:
        override_get_database_dependency: A callable that returns an instance
        of the test database handler.

    Yields:
        The FastAPI test application instance.
    """
    from app.api.dependencies import get_db_session
    from app.main import app

    app.dependency_overrides[get_db_session] = override_get_database_dependency
    yield app

    db_handler = get_test_db_handler()
    db_handler.drop_tables()
    db_handler.engine.dispose()


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Creates an asynchronous test client for FastAPI app.

    Args:
        app (FastAPI): The FastAPI application to which the client will send requests.

    Yields:
        AsyncClient: An instance of httpx.AsyncClient for making API requests.
    """
    async with AsyncClient(
            transport=ASGITransport(app=app),  # type: ignore[arg-type]
            base_url="http://testserver/api",
    ) as async_client:
        yield async_client


@pytest.fixture
def access_token() -> str:
    settings = Settings()
    user = 'johndoe'
    access_token_expires = timedelta(minutes=1)

    return UserAuthServices.create_access_token(
        data={"sub": user},
        expires_delta=access_token_expires,
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
