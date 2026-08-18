import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    bins,
    classifications,
    dcpi,
    digital_twin,
    health,
    kpis,
    predictions,
    routes_opt,
    telemetry,
    workers,
    xai,
)
from app.config import settings
from app.mqtt.listener import start_mqtt_listener
from app.services.dcpi_service import recompute_all_dcpi
from app.services.forecaster import recompute_forecasts
from app.services.wqs_service import recompute_all_wqs

logging.basicConfig(level=logging.INFO)
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = start_mqtt_listener()
    scheduler.add_job(recompute_all_dcpi, "interval", seconds=30, id="dcpi")
    scheduler.add_job(recompute_forecasts, "interval", minutes=5, id="forecast")
    scheduler.add_job(recompute_all_wqs, "interval", minutes=2, id="wqs")
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)
    task.cancel()


app = FastAPI(title="SmartWasteAI API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in [
    health,
    bins,
    telemetry,
    classifications,
    predictions,
    dcpi,
    routes_opt,
    xai,
    digital_twin,
    workers,
    kpis,
]:
    app.include_router(r.router)
