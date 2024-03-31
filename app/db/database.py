import logging

from sqlalchemy import create_engine, text, URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session, close_all_sessions

from app.db.models import BaseSQL

logger = logging.getLogger(__name__)


class DatabaseHandler:
    """
    A class to handle postgres database using SQLAlchemy.

    """

    def __init__(
            self,
            database: str,
            db_username: str,
            db_password: str,
            db_host: str,
            db_port: int
    ):
        """
        Initializes the connection to the PostgreSQL database.

        Args:
            database (str): The name of the database.
            db_username (str): The username for database authentication.
            db_password (str): The password for database authentication.
            db_host (str): The host address of the database server.
            db_port (int): The port number of the database server.
        """
        self.base = BaseSQL
        self.database = database
        self.db_username = db_username
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

        self.db_url = self._build_db_url()

        self.engine = create_engine(self.db_url)

    def _build_db_url(self) -> URL:
        """
        Builds the database URL.

        Returns:
            str: The constructed database URL.
        """
        return URL.create(
            drivername="postgresql",
            username=self.db_username,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.database,
        )

    def create_session(self) -> Session:
        """
        Establishes a new session with the database.

        Returns:
            Session: A database session.
        """
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)()

    def initialize(self):
        """
        Create all the tables.
        """
        try:
            self.base.metadata.create_all(bind=self.engine, checkfirst=True)
        except Exception as ex:
            logger.error(f'creating tables failed: {ex}')

    def health_check(self) -> bool:
        """
        Performs a health check on the database.

        Returns:
            bool: True if the database is accessible and operational, False otherwise.
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text('SELECT 1'))
                return bool(result.scalar())
        except SQLAlchemyError as ex:
            logger.error(f'Database health check failed: {ex}')
            return False

    def drop_tables(self) -> None:
        """
        Drops all tables in the database based on the SQLAlchemy models.
        """
        close_all_sessions()
        self.base.metadata.drop_all(bind=self.engine)
