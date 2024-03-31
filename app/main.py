from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.v1.routers.shipments import router as v1_shipments_routers
from app.api.common.health import router as health_check_routers
from app.api.common.users import router as user_routers
from app.config.base import Settings
from app.db.database import DatabaseHandler as Database

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup-event

    settings = Settings()

    db_handler = Database(
        database=settings.POSTGRES_DATABASE,
        db_username=settings.POSTGRES_USERNAME,
        db_password=settings.POSTGRES_PASSWORD,
        db_host=settings.POSTGRES_HOST,
        db_port=int(settings.POSTGRES_PORT)
    )
    db_handler.initialize()
    logger.info(f'Database Health-Check: {db_handler.health_check()}')

    yield

    # shutdown-event


app = FastAPI(lifespan=lifespan)
app.include_router(health_check_routers, prefix="/api")
app.include_router(user_routers, prefix="/api")
app.include_router(v1_shipments_routers, prefix="/api/v1")


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url="/docs")
