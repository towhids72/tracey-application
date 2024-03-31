from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, get_settings
from app.auth.exceptions import InvalidCredentialsError
from app.config.base import Settings
from app.db.exceptions import DatabaseIntegrityError
from app.auth.users import UserServices, UserAuthServices
from app.schemas.schema_users import Token, UserInDB, User

router = APIRouter(
    prefix='/user',
    tags=['User']
)


# Adding a JWT refresh token is feasible, depending on our security requirements
# and our strategy for managing user authentication and authorization.

@router.post(path='/token')
async def login_for_access_token(
        settings: Annotated[Settings, Depends(get_settings)],
        db: Annotated[Session, Depends(get_db_session)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    try:
        token = UserAuthServices.authenticate_user_and_create_token(
            db=db,
            username=form_data.username,
            password=form_data.password,
            access_token_expire_time=int(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

        return token
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials'
        )


@router.post(path='/register', response_model=User)
async def create_user(
        user: UserInDB,
        db: Annotated[Session, Depends(get_db_session)]
):
    try:
        created_user = UserServices.create_user(
            db=db,
            email=user.email,
            username=user.username,
            password=user.password,
        )

        return created_user
    except DatabaseIntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Could not create user!'
        )
