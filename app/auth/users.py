from datetime import timedelta, datetime, timezone
from logging import getLogger

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.exceptions import InvalidCredentialsError
from app.db.exceptions import DatabaseIntegrityError
from app.db.models import UserModel
from app.schemas.schema_users import Token, User

logger = getLogger(__name__)


class UserServices:
    """
    A class responsible for managing user-related operations.

    """

    @staticmethod
    def get_pwd_context() -> CryptContext:
        """
        Returns a CryptContext instance initialized with bcrypt scheme and auto-deprecation handling.

        """
        return CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def hashed_password(password: str) -> str:
        """
        Hashes the provided password using bcrypt encryption.

        Args:
            password (str): The password to be hashed.

        Returns:
            str: The hashed password.
        """
        pwd_context = UserServices.get_pwd_context()
        return pwd_context.hash(password)  # type: ignore

    @staticmethod
    def verify_user_password(
            plain_password: str,
            hashed_password: str | Column[str]
    ) -> bool:
        """
        Verifies if the plain password matches the hashed password using bcrypt encryption.

        Args:
            plain_password (str): The plain text password to be verified.
            hashed_password (str): The hashed password stored in the database.

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        pwd_context = UserServices.get_pwd_context()
        return pwd_context.verify(plain_password, hashed_password)  # type: ignore

    @staticmethod
    def create_user(
            db: Session,
            email: str,
            username: str,
            password: str
    ) -> User:
        """
        Creates a new user in the database with the provided email, username, and password.

        Args:
            db (Session): The database session.
            email (str): The email address of the user.
            username (str): The username of the user.
            password (str): The plain text password of the user.

        Returns:
            User: The newly created user object.

        Raises:
            sqlalchemy.exc.IntegrityError: If there is a conflict in uniqueness constraints,
            such as duplicate email or username.
        """
        try:
            db.add(
                UserModel(
                    email=email,
                    username=username,
                    password=UserServices.hashed_password(password)
                )
            )

            db.commit()

            return User(
                username=username,
                email=email
            )
        except IntegrityError as e:
            logger.error(e)
            db.rollback()
            raise DatabaseIntegrityError(message=str(e))

    @staticmethod
    def get_user(
            db: Session,
            username: str
    ) -> UserModel:
        """
        Retrieves a user from the database based on the provided username.

        Args:
            db (Session): The database session.
            username (str): The username of the user to retrieve.

        Returns:
            UserModel: The user object corresponding to the provided username.

        Raises:
            InvalidCredentialsError: If the user with the provided username does not exist.
        """
        user: UserModel = db.query(UserModel).where(UserModel.username == username).scalar()

        if not user:
            raise InvalidCredentialsError

        return user

    @staticmethod
    def authenticate_user(
            db: Session,
            username: str,
            password: str
    ) -> UserModel:
        """
        Authenticates a user based on the provided username and password.

        Args:
            db (Session): The database session.
            username (str): The username of the user to authenticate.
            password (str): The password of the user to authenticate.

        Returns:
            UserModel: The authenticated user object.

        Raises:
            InvalidCredentialsError: If the provided username or password is incorrect.
        """
        user = UserServices.get_user(db=db, username=username)

        if not UserServices.verify_user_password(password, user.password):
            raise InvalidCredentialsError

        return user


class UserAuthServices:
    """
    A class responsible for managing users authentication and authorization.

    """

    @staticmethod
    def create_access_token(
            data: dict,
            expires_delta: timedelta,
            secret_key: str,
            algorithm: str
    ) -> str:
        """
        Creates an access token with the provided data.

        Args:
            data (dict): The payload data to be encoded into the token.
            expires_delta (timedelta): The expiration delta for the token.
            secret_key (str): The secret key used for encoding the token.
            algorithm (str): The algorithm used for encoding the token.

        Returns:
            str: The encoded access token.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt: str = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt

    @staticmethod
    def authenticate_user_and_create_token(
            db: Session,
            username: str,
            password: str,
            access_token_expire_time: int,
            secret_key: str,
            algorithm: str
    ) -> Token:
        """
        Authenticates a user based on the provided username and password,
        and creates an access token for the authenticated user.

        Args:
            db (Session): The database session.
            username (str): The username of the user to authenticate.
            password (str): The password of the user to authenticate.
            access_token_expire_time (int): The expiration time for the access token in minutes.
            secret_key (str): The secret key used for encoding the access token.
            algorithm (str): The algorithm used for encoding the access token.

        Returns:
            Token: The access token and token type for the authenticated user.

        Raises:
            InvalidCredentialsError: If the provided username or password is incorrect.
        """
        user = UserServices.authenticate_user(
            db=db,
            username=username,
            password=password
        )

        access_token_expires = timedelta(minutes=access_token_expire_time)

        access_token = UserAuthServices.create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires,
            secret_key=secret_key,
            algorithm=algorithm
        )

        return Token(access_token=access_token, token_type="bearer")
