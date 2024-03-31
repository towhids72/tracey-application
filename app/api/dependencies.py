import json
from functools import lru_cache
from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.api.v1.schemas.schema_parcels import CarrierType
from app.config.base import Settings

from app.db.database import DatabaseHandler
from app.services.carrier.base import Carrier
from app.services.carrier.bpost import BPostCarrier
from app.services.carrier.dhl import DHLCarrier

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/user/token')


@lru_cache
def get_settings() -> Settings:
    """
    Retrieves the application settings.

    Returns:
        Settings: The application settings.

    Notes:
        This function is decorated with `lru_cache` to cache the result of
        the function call. Subsequent calls with the same arguments will
        return the cached result instead of reloading it, which can
        improve performance by reducing redundant file reading.
    """
    return Settings()


def validate_user_token(
        token: Annotated[str, Depends(oauth2_scheme)],
        settings: Annotated[Settings, Depends(get_settings)]
) -> str:
    """
    Validates the user token.

    Args:
        token (str): The user token to validate.
        settings (Settings): The application settings.

    Returns:
        str: The validated user's username.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials, please check your credentials and login again",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token=token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        return username

    except JWTError:
        raise credentials_exception


def get_db_session(settings: Annotated[Settings, Depends(get_settings)]) -> Generator[Session, None, None]:
    """
    Creates a new database session.

    Args:
        settings (Settings): The application settings.

    Returns:
        Session: The database session.
    """
    session = DatabaseHandler(
        database=settings.POSTGRES_DATABASE,
        db_username=settings.POSTGRES_USERNAME,
        db_password=settings.POSTGRES_PASSWORD,
        db_host=settings.POSTGRES_HOST,
        db_port=int(settings.POSTGRES_PORT)
    ).create_session()

    yield session


@lru_cache
def get_tracey_event_map() -> dict:
    """
    Retrieves the mapping of Tracey events.

    Returns:
        dict: A dictionary containing the mapping of Tracey events.

    Notes:
        This function is decorated with `lru_cache` to cache the result of
        the function call. Subsequent calls will return the cached result
        instead of reading it from file again, which can improve performance.
    """

    # Another approach could involve creating a dataclass for events.
    # The choice depends on the frequency of event changes or updates.
    # Alternatively, we could fetch them from a third-party API.
    # For simplicity, we're currently loading them from a provided file.

    with open('filtered_events.json', 'r') as event_map:
        return json.load(event_map)  # type: ignore[no-any-return]


def get_carrier_handler(
        carrier_type: CarrierType,
        tracking_number: str,
        settings: Annotated[Settings, Depends(get_settings)],
        tracey_event_map: Annotated[dict, Depends(get_tracey_event_map)]
) -> Carrier:
    """
    Instantiate a carrier handler based on the carrier type.

    Args:
        carrier_type (CarrierType): The type of carrier.
        tracking_number (str): The tracking number associated with the shipment.
        settings (Settings): The application settings.
        tracey_event_map (dict): The mapping of Tracey events.

    Returns:
        Carrier: The carrier handler object.

    Raises:
        ValueError: If an invalid carrier type has been selected.
    """
    if carrier_type is CarrierType.DHL:
        return DHLCarrier(
            tracking_number=tracking_number,
            api_key=settings.DHL_API_KEY,
            trace_event_map=tracey_event_map.get(carrier_type.DHL.value)  # type: ignore
        )

    if carrier_type is CarrierType.BPOST:
        return BPostCarrier(
            tracking_number=tracking_number,
            trace_event_map=tracey_event_map.get(carrier_type.BPOST.value)  # type: ignore
        )

    raise ValueError('Invalid carrier type has been selected!')
