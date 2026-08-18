from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BinOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    district: str
    lat: float
    lon: float
    capacity_l: int = 120
    hardware_id: str | None = None
    qr_code: str | None = None
    created_at: datetime | None = None


class BinCreate(BaseModel):
    name: str
    district: str
    lat: float
    lon: float
    capacity_l: int = 120
    hardware_id: str | None = None
    qr_code: str | None = None


class BinDetail(BinOut):
    fill_pct: float | None = None
    wqs: float | None = None
    dcpi: float | None = None
    last_classification: str | None = None


class TelemetryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ts: datetime
    bin_id: int
    fill_pct: float
    weight_kg: float
    temp_c: float
    humidity_pct: float
    gas_ppm: float
    source: str = "simulator"


class TelemetryLatest(TelemetryOut):
    bin_name: str | None = None
    district: str | None = None


class ClassificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bin_id: int
    ts: datetime
    waste_class: str
    confidence: float
    item_count: int = 1


class ClassificationCreate(BaseModel):
    bin_id: int
    waste_class: str
    confidence: float = 0.9
    item_count: int = 1


class PredictionPoint(BaseModel):
    ts_target: datetime
    predicted_fill_pct: float
    horizon_hours: int


class PredictionCurve(BaseModel):
    bin_id: int
    points: list[PredictionPoint]


class DCPIItem(BaseModel):
    bin_id: int
    name: str
    district: str
    lat: float
    lon: float
    dcpi: float
    ts: datetime


class DCPIDetail(BaseModel):
    bin_id: int
    dcpi: float
    ts: datetime
    features: dict[str, float]
    reasons: list[dict[str, Any]]


class RouteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ts: datetime
    truck_id: str
    stops: list[int]
    distance_km: float
    expected_fuel_saving_pct: float
    expected_co2_saving_kg: float


class XAIExplanationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dcpi_id: int
    natural_language: str
    features: list[Any]


class WorkerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    district: str
    active: bool = True


class CollectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    worker_id: int
    bin_id: int
    ts: datetime
    qr_scan: str
    weight_kg: float
    payment_amount: Decimal


class ScanRequest(BaseModel):
    qr_code: str
    weight_kg: float = Field(default=2.5, ge=0)


class SimulationRequest(BaseModel):
    scenario: str = "festival"
    district: str | None = None
    event_multiplier: float = 2.0
    duration_hours: int = 4


class SimulationResult(BaseModel):
    scenario: str
    district: str | None
    bins_affected: int
    avg_dcpi_before: float
    avg_dcpi_after: float
    message: str


class KPISummary(BaseModel):
    bins_total: int
    overflow_risk_avg: float
    wqs_avg: float
    co2_avoided_kg: float
    cost_saved_pct: float
    workers_active: int
    payments_today: float


class HealthOut(BaseModel):
    status: str = "ok"
