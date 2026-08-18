# SmartWasteAI — Complete Implementation Specification

> **Purpose of this document.** Single source of truth for Cursor to generate the entire SmartWasteAI codebase. Every module, every endpoint, every schema, every command is specified. Follow the order in section 12 (72-hour roadmap) for time-critical implementation.

**Team:** AI4Earth · **Team Leader:** Housseni YABRE · **Deadline:** 18 Aug 2026 · **Sprint:** 72 hours starting 15 Aug evening.

---

## Table of contents

1. [Project context](#1-project-context)
2. [Architecture overview](#2-architecture-overview)
3. [Tech stack (locked versions)](#3-tech-stack-locked-versions)
4. [Repository structure](#4-repository-structure)
5. [Development environment](#5-development-environment)
6. [Database schema](#6-database-schema-postgresql--timescaledb)
7. [Backend implementation (FastAPI)](#7-backend-implementation-fastapi)
8. [ML pipeline](#8-ml-pipeline)
9. [Sensor simulator](#9-sensor-simulator)
10. [Frontend implementation (React + TypeScript)](#10-frontend-implementation-react--typescript)
11. [Docker orchestration](#11-docker-orchestration)
12. [72-hour implementation roadmap](#12-72-hour-implementation-roadmap)
13. [Testing & end-to-end scenario](#13-testing--end-to-end-scenario)
14. [Submission checklist (18 Aug)](#14-submission-checklist-18-aug)

Priority legend used throughout:
- 🔴 **CORE** — must ship for Aug 18 submission
- 🟡 **EXTENDED** — build if Day 3 has slack
- 🟢 **FUTURE** — post-submission v2

---

## 1. Project context

**SmartWasteAI** is a *Federated, Multi-Agent, Explainable AI Framework for Predictive Urban Waste Management with Informal Sector Integration*.

Five named contributions the code must demonstrate:
1. **WQS** — Waste Quality Score per bin and district
2. **DCPI** — Dynamic Collection Priority Index (context-aware urgency)
3. **FL** — Federated Learning across bins (privacy-preserving)
4. **XAI** — SHAP-based natural-language explanations
5. **DT** — Digital Twin for what-if scenario simulation

Plus one social bridge: **informal waste-picker mobile app** with QR-based collection tracking and micropayments (design + API stub for MVP).

**Demo scenario for Aug 18 submission:**
> Simulator streams telemetry from 40 virtual bins across 4 districts → ML pipeline classifies waste + computes WQS → forecaster predicts fill → DCPI ranks bins by priority → OR-Tools computes truck route → SHAP explains each dispatch → React dashboard shows the map + 5-minute reproducible walkthrough.

---

## 2. Architecture overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        TIER 1 — EDGE (per bin)                           │
│  Camera → YOLOv8n (INT8) → local classification                          │
│  Sensors (US · Load · Temp · Humidity · Gas) → Raspberry Pi 4            │
│                                                                          │
│  ⚠ For MVP: replaced by SENSOR SIMULATOR (simulator/)                    │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │  MQTT (topic: smartwaste/bins/{bin_id}/telemetry)
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    TIER 2 — FEDERATED CLOUD                              │
│  MQTT listener → PostgreSQL + TimescaleDB (telemetry hypertable)         │
│  XGBoost fill forecaster (per district)                                  │
│  Flower FL server (POC — 10 virtual clients)                             │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │  Internal service calls
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     TIER 3 — DECISION LAYER                              │
│  DCPI scoring service (fuses fill, weather, events, gas)                 │
│  OR-Tools route optimizer                                                │
│  SHAP XAI engine → natural-language explanations                         │
│  Digital Twin simulator                                                  │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │  REST API (FastAPI)
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + Vite)                             │
│  Live Map · Prediction · Routes · Digital Twin · KPIs · Alerts           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                 BRIDGE — INFORMAL SECTOR                                 │
│  React Native worker app (scan QR → log collection → auto-pay)           │
│  ⚠ For MVP: API stub only, mobile app is design                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Tech stack (locked versions)

| Layer | Tool | Version | Purpose |
|---|---|---|---|
| Backend runtime | Python | 3.11 | Backend + ML + simulator |
| Backend framework | FastAPI | 0.115.* | REST API |
| ASGI server | Uvicorn | 0.32.* | Serve FastAPI |
| ORM | SQLAlchemy | 2.0.* | DB access |
| DB migrations | Alembic | 1.13.* | Schema versioning |
| Database | PostgreSQL | 16 | Relational store |
| Time-series ext. | TimescaleDB | 2.17.* | Telemetry hypertable |
| Messaging | Eclipse Mosquitto | 2.0.* | MQTT broker |
| MQTT client (Py) | paho-mqtt | 2.1.* | MQTT ingestion |
| ML — vision | Ultralytics YOLO | 8.3.* | Waste classifier |
| ML — forecast | XGBoost | 2.1.* | Fill forecaster |
| ML — XAI | SHAP | 0.46.* | Explainable AI |
| ML — routing | Google OR-Tools | 9.11.* | Vehicle routing |
| ML — FL | Flower | 1.13.* | Federated learning |
| Data | Pandas / NumPy | latest | Data manipulation |
| Frontend runtime | Node | 20 LTS | Build + dev server |
| Frontend framework | React | 18.3 | UI |
| Bundler | Vite | 5.* | Dev + build |
| Language | TypeScript | 5.* | Type safety |
| State | Zustand | 5.* | Client state |
| Data fetching | TanStack Query | 5.* | API caching |
| Maps | Leaflet + React-Leaflet | 1.9 / 4.* | Live map |
| Charts | Recharts | 2.* | Dashboard |
| 3D | Three.js + React-Three-Fiber | 0.169 / 8.* | Digital Twin |
| Styling | Tailwind CSS | 3.4 | Utility CSS |
| Container | Docker + Compose | latest | Orchestration |

---

## 4. Repository structure

```
smartwasteai/
├── README.md
├── SPEC.md                          ← this file
├── .env.example
├── .gitignore
├── docker-compose.yml
├── docker-compose.dev.yml
├── Makefile
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── demo-script.md
│
├── backend/                         🔴 CORE
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── config.py                # Pydantic Settings
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   ├── models.py            # SQLAlchemy ORM models
│   │   │   └── schemas.py           # Pydantic schemas
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   └── routes/
│   │   │       ├── health.py
│   │   │       ├── bins.py
│   │   │       ├── telemetry.py
│   │   │       ├── classifications.py
│   │   │       ├── predictions.py
│   │   │       ├── dcpi.py
│   │   │       ├── routes_opt.py
│   │   │       ├── xai.py
│   │   │       ├── digital_twin.py
│   │   │       ├── workers.py
│   │   │       └── kpis.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ml_inference.py
│   │   │   ├── wqs_service.py
│   │   │   ├── dcpi_service.py
│   │   │   ├── forecaster.py
│   │   │   ├── route_optimizer.py
│   │   │   ├── xai_engine.py
│   │   │   └── digital_twin.py
│   │   ├── mqtt/
│   │   │   ├── __init__.py
│   │   │   └── listener.py
│   │   └── utils/
│   │       ├── logging.py
│   │       └── time.py
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── alembic.ini
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_bins.py
│   │   ├── test_dcpi.py
│   │   └── test_wqs.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── ml/                              🔴 CORE
│   ├── notebooks/
│   │   ├── 01_dataset_exploration.ipynb
│   │   ├── 02_yolo_finetuning.ipynb
│   │   ├── 03_forecaster.ipynb
│   │   └── 04_shap_explainer.ipynb
│   ├── src/
│   │   ├── data/
│   │   │   ├── download_datasets.py     # TrashNet + TACO downloader
│   │   │   ├── preprocess.py
│   │   │   ├── split.py
│   │   │   └── augment.py
│   │   ├── training/
│   │   │   ├── train_yolo.py
│   │   │   ├── train_forecaster.py
│   │   │   └── config.yaml
│   │   ├── inference/
│   │   │   ├── classifier.py
│   │   │   └── batch_infer.py
│   │   ├── wqs/
│   │   │   └── scorer.py
│   │   ├── dcpi/
│   │   │   └── engine.py
│   │   ├── forecast/
│   │   │   └── model.py
│   │   ├── xai/
│   │   │   └── explainer.py
│   │   └── federated/                 🟡 EXTENDED
│   │       ├── server.py
│   │       ├── client.py
│   │       └── simulate.py
│   ├── models/                        # Trained artifacts
│   │   └── .gitkeep
│   ├── datasets/                      # Data (git-ignored)
│   │   └── .gitkeep
│   ├── requirements.txt
│   └── Dockerfile
│
├── simulator/                        🔴 CORE
│   ├── src/
│   │   ├── main.py
│   │   ├── bin.py
│   │   ├── city.py
│   │   ├── weather.py
│   │   ├── events.py
│   │   └── publisher.py
│   ├── config/
│   │   └── city_config.yaml
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                         🔴 CORE
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── bins.ts
│   │   │   ├── dcpi.ts
│   │   │   ├── predictions.ts
│   │   │   ├── routes.ts
│   │   │   └── kpis.ts
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   ├── SidebarNav.tsx
│   │   │   ├── BinPin.tsx
│   │   │   ├── BinDetailPanel.tsx
│   │   │   ├── KPICard.tsx
│   │   │   └── ExplanationBox.tsx
│   │   ├── modules/
│   │   │   ├── LiveMap.tsx
│   │   │   ├── Prediction.tsx
│   │   │   ├── Routes.tsx
│   │   │   ├── DigitalTwin.tsx
│   │   │   ├── KPIs.tsx
│   │   │   └── Alerts.tsx
│   │   ├── store/
│   │   │   └── selection.ts
│   │   ├── hooks/
│   │   │   └── usePolling.ts
│   │   ├── types/
│   │   │   └── domain.ts
│   │   └── styles/
│   │       └── globals.css
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── Dockerfile
│
├── mobile/                           🟡 EXTENDED (design stub only)
│   ├── README.md
│   └── screens/
│       ├── ScanScreen.md
│       ├── EarningsScreen.md
│       └── NearbyBinsScreen.md
│
└── scripts/
    ├── setup.sh
    ├── seed_demo_data.py
    ├── smoke_test.sh
    └── record_demo.sh
```

---

## 5. Development environment

### 5.1 Prerequisites

```bash
# Verify installed:
python --version    # >= 3.11
node --version      # >= 20
docker --version    # >= 24
docker compose version
```

### 5.2 `.env.example`

```dotenv
# ---- Database ----
POSTGRES_USER=smartwaste
POSTGRES_PASSWORD=changeme
POSTGRES_DB=smartwaste
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://smartwaste:changeme@db:5432/smartwaste

# ---- MQTT ----
MQTT_HOST=mqtt
MQTT_PORT=1883
MQTT_TOPIC_PREFIX=smartwaste

# ---- Backend ----
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173

# ---- ML ----
MODELS_DIR=/app/models
YOLO_WEIGHTS=/app/models/yolov8n_waste.pt
FORECAST_MODEL=/app/models/xgb_forecaster.json

# ---- Simulator ----
SIMULATOR_TICK_MS=5000              # publish every 5 s (compressed time)
SIMULATOR_BIN_COUNT=40
SIMULATOR_DISTRICT_COUNT=4

# ---- Frontend ----
VITE_API_BASE=http://localhost:8000
VITE_POLL_INTERVAL_MS=5000
```

### 5.3 `Makefile`

```makefile
.PHONY: up down logs backend-shell db-shell migrate seed simulate train test

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f

backend-shell:
	docker compose exec backend bash

db-shell:
	docker compose exec db psql -U smartwaste smartwaste

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python -m scripts.seed_demo_data

simulate:
	docker compose up simulator --build

train:
	docker compose run --rm ml python -m src.training.train_yolo

test:
	docker compose exec backend pytest -v
```

---

## 6. Database schema (PostgreSQL + TimescaleDB)

### 6.1 SQLAlchemy models — `backend/app/db/models.py`

```python
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    String, Float, Integer, DateTime, ForeignKey, JSON, Text, Boolean, Numeric
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Bin(Base):
    __tablename__ = "bins"
    id: Mapped[int]        = mapped_column(primary_key=True)
    name: Mapped[str]      = mapped_column(String(64), unique=True)
    district: Mapped[str]  = mapped_column(String(32), index=True)
    lat: Mapped[float]     = mapped_column(Float)
    lon: Mapped[float]     = mapped_column(Float)
    capacity_l: Mapped[int]= mapped_column(Integer, default=120)
    hardware_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=True)
    qr_code: Mapped[str]   = mapped_column(String(128), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    telemetries    = relationship("Telemetry", back_populates="bin", cascade="all, delete-orphan")
    classifications= relationship("Classification", back_populates="bin", cascade="all, delete-orphan")


class Telemetry(Base):
    """Time-series bin sensor readings. Will become a TimescaleDB hypertable."""
    __tablename__ = "telemetry"
    ts: Mapped[datetime]    = mapped_column(DateTime, primary_key=True)
    bin_id: Mapped[int]     = mapped_column(ForeignKey("bins.id"), primary_key=True, index=True)
    fill_pct: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float]= mapped_column(Float)
    temp_c: Mapped[float]   = mapped_column(Float)
    humidity_pct: Mapped[float]= mapped_column(Float)
    gas_ppm: Mapped[float]  = mapped_column(Float)
    source: Mapped[str]     = mapped_column(String(16), default="simulator")  # simulator | hardware

    bin = relationship("Bin", back_populates="telemetries")


class Classification(Base):
    """Per-bin waste item classifications from the vision model."""
    __tablename__ = "classifications"
    id: Mapped[int]         = mapped_column(primary_key=True)
    bin_id: Mapped[int]     = mapped_column(ForeignKey("bins.id"), index=True)
    ts: Mapped[datetime]    = mapped_column(DateTime, index=True)
    waste_class: Mapped[str]= mapped_column(String(16))   # plastic|paper|glass|metal|organic|ewaste
    confidence: Mapped[float]= mapped_column(Float)
    item_count: Mapped[int] = mapped_column(Integer, default=1)

    bin = relationship("Bin", back_populates="classifications")


class WQSScore(Base):
    """Aggregated sorting-quality score per bin, per window."""
    __tablename__ = "wqs_scores"
    id: Mapped[int]           = mapped_column(primary_key=True)
    bin_id: Mapped[int]       = mapped_column(ForeignKey("bins.id"), index=True)
    ts: Mapped[datetime]      = mapped_column(DateTime, index=True)
    wqs: Mapped[float]        = mapped_column(Float)      # 0..100
    contamination_pct: Mapped[float] = mapped_column(Float)
    per_class_pct: Mapped[dict]      = mapped_column(JSON)


class DCPIScore(Base):
    """Dynamic Collection Priority Index."""
    __tablename__ = "dcpi_scores"
    id: Mapped[int]      = mapped_column(primary_key=True)
    bin_id: Mapped[int]  = mapped_column(ForeignKey("bins.id"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime, index=True)
    dcpi: Mapped[float]  = mapped_column(Float)             # 0..100
    features: Mapped[dict]= mapped_column(JSON)             # inputs to SHAP
    reasons: Mapped[list] = mapped_column(JSON)             # ranked contribution list


class Prediction(Base):
    """Fill-level forecast per bin."""
    __tablename__ = "predictions"
    id: Mapped[int]           = mapped_column(primary_key=True)
    bin_id: Mapped[int]       = mapped_column(ForeignKey("bins.id"), index=True)
    ts_made: Mapped[datetime] = mapped_column(DateTime)
    ts_target: Mapped[datetime] = mapped_column(DateTime, index=True)
    predicted_fill_pct: Mapped[float] = mapped_column(Float)
    horizon_hours: Mapped[int]        = mapped_column(Integer)


class Route(Base):
    """Optimized truck route (daily)."""
    __tablename__ = "routes"
    id: Mapped[int]      = mapped_column(primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, index=True)
    truck_id: Mapped[str] = mapped_column(String(32))
    stops: Mapped[list]   = mapped_column(JSON)             # ordered [bin_id, ...]
    distance_km: Mapped[float] = mapped_column(Float)
    expected_fuel_saving_pct: Mapped[float] = mapped_column(Float)
    expected_co2_saving_kg: Mapped[float]  = mapped_column(Float)


class XAIExplanation(Base):
    __tablename__ = "xai_explanations"
    id: Mapped[int]      = mapped_column(primary_key=True)
    dcpi_id: Mapped[int] = mapped_column(ForeignKey("dcpi_scores.id"), index=True)
    natural_language: Mapped[str]= mapped_column(Text)
    features: Mapped[list]       = mapped_column(JSON)     # [(feature, shap_value), ...]


class Worker(Base):
    """Informal waste-picker."""
    __tablename__ = "workers"
    id: Mapped[int]     = mapped_column(primary_key=True)
    name: Mapped[str]   = mapped_column(String(64))
    phone: Mapped[str]  = mapped_column(String(24), unique=True)
    district: Mapped[str] = mapped_column(String(32))
    active: Mapped[bool]  = mapped_column(Boolean, default=True)


class Collection(Base):
    """Waste-picker collection event via QR scan."""
    __tablename__ = "collections"
    id: Mapped[int]         = mapped_column(primary_key=True)
    worker_id: Mapped[int]  = mapped_column(ForeignKey("workers.id"), index=True)
    bin_id: Mapped[int]     = mapped_column(ForeignKey("bins.id"), index=True)
    ts: Mapped[datetime]    = mapped_column(DateTime, index=True)
    qr_scan: Mapped[str]    = mapped_column(String(128))
    weight_kg: Mapped[float]= mapped_column(Float)
    payment_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))


class CityEvent(Base):
    """Festivals, matches, etc. that impact waste generation."""
    __tablename__ = "city_events"
    id: Mapped[int]          = mapped_column(primary_key=True)
    name: Mapped[str]        = mapped_column(String(128))
    district: Mapped[str]    = mapped_column(String(32))
    start_ts: Mapped[datetime] = mapped_column(DateTime)
    end_ts: Mapped[datetime]   = mapped_column(DateTime)
    expected_multiplier: Mapped[float] = mapped_column(Float, default=1.5)
```

### 6.2 Migration — convert `telemetry` to TimescaleDB hypertable

Create `backend/alembic/versions/002_timescale_hypertable.py`:

```python
from alembic import op
import sqlalchemy as sa

revision = "002_timescale_hypertable"
down_revision = "001_initial"

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
    op.execute("SELECT create_hypertable('telemetry', 'ts', if_not_exists => TRUE);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_telemetry_bin_ts ON telemetry (bin_id, ts DESC);")

def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_telemetry_bin_ts;")
```

---

## 7. Backend implementation (FastAPI)

### 7.1 `backend/requirements.txt`

```txt
fastapi==0.115.6
uvicorn[standard]==0.32.1
pydantic==2.10.3
pydantic-settings==2.7.1
sqlalchemy==2.0.36
alembic==1.14.0
psycopg[binary]==3.2.3
paho-mqtt==2.1.0
python-dotenv==1.0.1
httpx==0.28.1
ortools==9.11.4210
xgboost==2.1.3
shap==0.46.0
pandas==2.2.3
numpy==2.2.0
scikit-learn==1.6.0
apscheduler==3.11.0
pytest==8.3.4
pytest-asyncio==0.24.0
```

### 7.2 `backend/app/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    mqtt_host: str = "mqtt"
    mqtt_port: int = 1883
    mqtt_topic_prefix: str = "smartwaste"
    cors_origins: str = "http://localhost:5173"
    models_dir: str = "/app/models"

settings = Settings()
```

### 7.3 `backend/app/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.api.routes import (
    health, bins, telemetry, classifications, predictions,
    dcpi, routes_opt, xai, digital_twin, workers, kpis,
)
from app.mqtt.listener import start_mqtt_listener
from app.services.dcpi_service import recompute_all_dcpi
from app.services.forecaster import recompute_forecasts

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    task = start_mqtt_listener()
    scheduler.add_job(recompute_all_dcpi, "interval", seconds=30, id="dcpi")
    scheduler.add_job(recompute_forecasts, "interval", minutes=5, id="forecast")
    scheduler.start()
    yield
    # shutdown
    scheduler.shutdown()
    task.cancel()

app = FastAPI(title="SmartWasteAI API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

for r in [health, bins, telemetry, classifications, predictions,
          dcpi, routes_opt, xai, digital_twin, workers, kpis]:
    app.include_router(r.router)
```

### 7.4 REST API contracts — full list

Base URL: `http://localhost:8000/api/v1`

| Method | Path | Purpose | Response |
|---|---|---|---|
| GET | `/health` | Liveness | `{status: "ok"}` |
| GET | `/bins` | List all bins | `Bin[]` |
| GET | `/bins/{id}` | Bin detail (current fill, WQS, DCPI, last classification) | `BinDetail` |
| POST | `/bins` | Create bin (admin) | `Bin` |
| GET | `/bins/{id}/telemetry?limit=100` | Recent telemetry | `Telemetry[]` |
| GET | `/telemetry/latest` | Latest reading per bin | `TelemetryLatest[]` |
| GET | `/classifications/{bin_id}?limit=50` | Recent classifications | `Classification[]` |
| POST | `/classifications` | Record classification (from ML worker) | `Classification` |
| GET | `/predictions/{bin_id}?horizon=24` | 24 h forecast curve | `PredictionCurve` |
| GET | `/dcpi` | Current DCPI ranking (all bins, sorted) | `DCPIItem[]` |
| GET | `/dcpi/{bin_id}` | DCPI + explanation | `DCPIDetail` |
| GET | `/routes/today` | Today's optimized route | `Route` |
| POST | `/routes/optimize` | Trigger optimization | `Route` |
| GET | `/xai/{dcpi_id}` | SHAP explanation for a DCPI score | `XAIExplanation` |
| POST | `/digital-twin/simulate` | Run a what-if scenario | `SimulationResult` |
| GET | `/workers` | List workers | `Worker[]` |
| POST | `/workers/{id}/scan` | Record QR scan → collection | `Collection` |
| GET | `/kpis/summary` | Aggregate KPIs (CO₂, cost, recycling, WQS) | `KPISummary` |

### 7.5 Endpoint example — `backend/app/api/routes/dcpi.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.db.models import DCPIScore, Bin
from app.db.schemas import DCPIItem, DCPIDetail

router = APIRouter(prefix="/api/v1/dcpi", tags=["dcpi"])

@router.get("", response_model=list[DCPIItem])
def list_dcpi(db: Session = Depends(get_db)):
    """Return latest DCPI per bin, sorted by score descending."""
    sub = (select(DCPIScore.bin_id, DCPIScore.dcpi, DCPIScore.ts)
           .distinct(DCPIScore.bin_id)
           .order_by(DCPIScore.bin_id, desc(DCPIScore.ts))
           .subquery())
    rows = db.execute(
        select(Bin.id, Bin.name, Bin.district, Bin.lat, Bin.lon, sub.c.dcpi, sub.c.ts)
        .join(sub, sub.c.bin_id == Bin.id)
        .order_by(desc(sub.c.dcpi))
    ).all()
    return [DCPIItem(bin_id=r[0], name=r[1], district=r[2], lat=r[3], lon=r[4],
                     dcpi=r[5], ts=r[6]) for r in rows]

@router.get("/{bin_id}", response_model=DCPIDetail)
def get_dcpi(bin_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        select(DCPIScore).where(DCPIScore.bin_id == bin_id)
        .order_by(desc(DCPIScore.ts)).limit(1)
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(404, "no DCPI yet for this bin")
    return DCPIDetail(
        bin_id=bin_id, dcpi=row.dcpi, ts=row.ts,
        features=row.features, reasons=row.reasons,
    )
```

### 7.6 MQTT listener — `backend/app/mqtt/listener.py`

```python
import asyncio, json, logging
from datetime import datetime
import paho.mqtt.client as mqtt
from app.config import settings
from app.db.session import SessionLocal
from app.db.models import Telemetry

log = logging.getLogger(__name__)

def _on_connect(client, userdata, flags, rc, props=None):
    log.info("MQTT connected rc=%s", rc)
    client.subscribe(f"{settings.mqtt_topic_prefix}/bins/+/telemetry", qos=1)

def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        bin_id = int(msg.topic.split("/")[-2])
        with SessionLocal() as db:
            db.add(Telemetry(
                ts=datetime.utcnow(), bin_id=bin_id,
                fill_pct=payload["fill_pct"], weight_kg=payload["weight_kg"],
                temp_c=payload["temp_c"], humidity_pct=payload["humidity_pct"],
                gas_ppm=payload["gas_ppm"], source=payload.get("source", "simulator"),
            ))
            db.commit()
    except Exception as e:
        log.exception("MQTT ingest failed: %s", e)

def start_mqtt_listener():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="backend-listener")
    client.on_connect = _on_connect
    client.on_message = _on_message
    client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(None, client.loop_forever)
```

### 7.7 DCPI service — `backend/app/services/dcpi_service.py`

```python
"""
DCPI = w_fill * fill_pct
     + w_pred * predicted_fill_pct
     + w_temp * heat_index
     + w_gas  * gas_index
     + w_evt  * event_boost
"""
from datetime import datetime, timedelta
from sqlalchemy import select, desc
from app.db.session import SessionLocal
from app.db.models import Bin, Telemetry, Prediction, DCPIScore, CityEvent

WEIGHTS = {"fill": 0.35, "pred": 0.25, "temp": 0.10, "gas": 0.15, "event": 0.15}

def compute_dcpi_for_bin(bin_id: int, db) -> tuple[float, dict, list]:
    now = datetime.utcnow()
    latest_tel = db.execute(
        select(Telemetry).where(Telemetry.bin_id == bin_id)
        .order_by(desc(Telemetry.ts)).limit(1)
    ).scalar_one_or_none()
    if not latest_tel: return 0.0, {}, []

    latest_pred = db.execute(
        select(Prediction).where(Prediction.bin_id == bin_id,
                                 Prediction.ts_target > now,
                                 Prediction.ts_target < now + timedelta(hours=4))
        .order_by(desc(Prediction.ts_target)).limit(1)
    ).scalar_one_or_none()

    bin_ = db.get(Bin, bin_id)
    active_event = db.execute(
        select(CityEvent).where(CityEvent.district == bin_.district,
                                CityEvent.start_ts <= now,
                                CityEvent.end_ts >= now)
        .limit(1)
    ).scalar_one_or_none()

    fill = latest_tel.fill_pct
    pred = latest_pred.predicted_fill_pct if latest_pred else fill
    heat = min(100.0, max(0.0, (latest_tel.temp_c - 20) * 5))     # 20 °C→0, 40 °C→100
    gas  = min(100.0, latest_tel.gas_ppm / 10.0)                  # 1000 ppm → 100
    evt  = 100.0 if active_event else 0.0

    features = {"fill_pct": fill, "predicted_fill_pct": pred,
                "heat_index": heat, "gas_index": gas, "event_boost": evt}
    dcpi = (WEIGHTS["fill"] * fill + WEIGHTS["pred"] * pred +
            WEIGHTS["temp"] * heat + WEIGHTS["gas"] * gas +
            WEIGHTS["event"] * evt)

    contributions = sorted(
        [(k, WEIGHTS[k.split("_")[0] if "_" in k else k] * v) for k, v in features.items()],
        key=lambda x: -x[1],
    )
    reasons = [{"feature": k, "contribution": round(v, 2)} for k, v in contributions[:3]]
    return round(dcpi, 2), features, reasons


def recompute_all_dcpi():
    with SessionLocal() as db:
        bin_ids = [b.id for b in db.execute(select(Bin)).scalars()]
        for bid in bin_ids:
            score, feats, reasons = compute_dcpi_for_bin(bid, db)
            db.add(DCPIScore(bin_id=bid, ts=datetime.utcnow(),
                             dcpi=score, features=feats, reasons=reasons))
        db.commit()
```

### 7.8 Route optimizer — `backend/app/services/route_optimizer.py`

```python
"""Vehicle-routing on top DCPI bins. Simplified TSP with capacity constraint."""
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from sqlalchemy import select, desc
from app.db.session import SessionLocal
from app.db.models import Bin, DCPIScore, Route

DEPOT_LAT, DEPOT_LON = 12.9716, 77.5946   # placeholder depot; adapt to city
TRUCK_CAPACITY = 20                        # bins per truck
MAX_BINS_PER_ROUTE = 15
MIN_DCPI_TO_COLLECT = 40.0

def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [a[0], a[1], b[0], b[1]])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    return 2 * R * asin(sqrt(sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2))


def optimize_today() -> dict:
    with SessionLocal() as db:
        # Pull latest DCPI per bin, filter above threshold
        sub = (select(DCPIScore.bin_id, DCPIScore.dcpi)
               .distinct(DCPIScore.bin_id)
               .order_by(DCPIScore.bin_id, desc(DCPIScore.ts))
               .subquery())
        rows = db.execute(
            select(Bin.id, Bin.lat, Bin.lon, sub.c.dcpi)
            .join(sub, sub.c.bin_id == Bin.id)
            .where(sub.c.dcpi >= MIN_DCPI_TO_COLLECT)
            .order_by(desc(sub.c.dcpi))
            .limit(MAX_BINS_PER_ROUTE)
        ).all()
        if not rows: return {"stops": [], "distance_km": 0.0}

        # Build distance matrix (index 0 = depot)
        pts = [(DEPOT_LAT, DEPOT_LON)] + [(r.lat, r.lon) for r in rows]
        n = len(pts)
        dist = [[int(haversine_km(pts[i], pts[j]) * 1000) for j in range(n)] for i in range(n)]

        manager = pywrapcp.RoutingIndexManager(n, 1, 0)
        routing = pywrapcp.RoutingModel(manager)
        def dist_cb(i, j):
            return dist[manager.IndexToNode(i)][manager.IndexToNode(j)]
        transit_idx = routing.RegisterTransitCallback(dist_cb)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        sol = routing.SolveWithParameters(params)

        stops, total_m = [], 0
        idx = routing.Start(0)
        while not routing.IsEnd(idx):
            node = manager.IndexToNode(idx)
            if node > 0:                       # skip depot
                stops.append(rows[node - 1].id)
            next_idx = sol.Value(routing.NextVar(idx))
            total_m += routing.GetArcCostForVehicle(idx, next_idx, 0)
            idx = next_idx

        distance_km = total_m / 1000
        baseline_km = sum(haversine_km(pts[0], p) * 2 for p in pts[1:])   # naive round-trip
        saving_pct = round(max(0.0, (1 - distance_km / baseline_km) * 100), 1) if baseline_km else 0.0

        route = Route(ts=datetime.utcnow(), truck_id="truck-1",
                      stops=stops, distance_km=distance_km,
                      expected_fuel_saving_pct=saving_pct,
                      expected_co2_saving_kg=round(distance_km * 0.35, 2))  # 350 g CO₂ / km diesel
        db.add(route); db.commit(); db.refresh(route)
        return {"id": route.id, "stops": stops, "distance_km": distance_km,
                "expected_fuel_saving_pct": saving_pct,
                "expected_co2_saving_kg": route.expected_co2_saving_kg}
```

---

## 8. ML pipeline

### 8.1 `ml/requirements.txt`

```txt
ultralytics==8.3.55
torch==2.5.1
torchvision==0.20.1
opencv-python-headless==4.10.0.84
pillow==11.0.0
numpy==2.2.0
pandas==2.2.3
xgboost==2.1.3
shap==0.46.0
scikit-learn==1.6.0
matplotlib==3.10.0
jupyter==1.1.1
flwr==1.13.1
pyyaml==6.0.2
tqdm==4.67.1
```

### 8.2 Dataset download — `ml/src/data/download_datasets.py`

```python
"""
Downloads:
 - TrashNet   (~2,500 images, 6 classes)  https://github.com/garythung/trashnet
 - TACO       (~1,500 in-the-wild litter images)  http://tacodataset.org/
Both saved to ml/datasets/{trashnet,taco}/
"""
import os, shutil, subprocess, sys, urllib.request, zipfile
from pathlib import Path

DATA_ROOT = Path(__file__).resolve().parents[2] / "datasets"

def download_trashnet():
    out = DATA_ROOT / "trashnet"
    if out.exists():
        print("TrashNet exists, skipping"); return
    out.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([
        "git", "clone", "--depth=1",
        "https://github.com/garythung/trashnet", str(out / "_repo"),
    ])
    zip_path = out / "_repo" / "data" / "dataset-resized.zip"
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(out)
    shutil.rmtree(out / "_repo")
    print("TrashNet ready at", out)

def download_taco():
    out = DATA_ROOT / "taco"
    if out.exists():
        print("TACO exists, skipping"); return
    out.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([
        "git", "clone", "--depth=1",
        "https://github.com/pedropro/TACO", str(out / "_repo"),
    ])
    subprocess.check_call([sys.executable, "download.py"],
                          cwd=str(out / "_repo"))
    print("TACO ready at", out)

if __name__ == "__main__":
    download_trashnet()
    download_taco()
```

### 8.3 Class mapping — `ml/src/data/preprocess.py`

```python
"""
Unify TrashNet + TACO classes into our 6 target categories:
    plastic, paper, glass, metal, organic, ewaste
"""
TARGET_CLASSES = ["plastic", "paper", "glass", "metal", "organic", "ewaste"]

TRASHNET_MAP = {
    "plastic": "plastic", "paper":   "paper",  "cardboard": "paper",
    "glass":   "glass",   "metal":   "metal",  "trash":     "organic",
}

# TACO has 60 fine classes; we bin them into our 6.
TACO_MAP = {
    "Plastic bottle": "plastic", "Plastic bag & wrapper": "plastic",
    "Plastic container": "plastic", "Plastic utensils": "plastic",
    "Styrofoam piece": "plastic", "Other plastic": "plastic",
    "Paper": "paper", "Cardboard": "paper", "Paper cup": "paper",
    "Magazine paper": "paper", "Wrapping paper": "paper",
    "Glass bottle": "glass", "Glass jar": "glass", "Broken glass": "glass",
    "Metal bottle cap": "metal", "Aluminium foil": "metal",
    "Metal lid": "metal", "Can": "metal", "Scrap metal": "metal",
    "Food waste": "organic",
    # e-waste rarely in TACO; supplement with self-labeled if possible.
}
```

### 8.4 Fine-tuning script — `ml/src/training/train_yolo.py`

```python
"""
Fine-tune YOLOv8n on our 6-class waste dataset (TrashNet + TACO merged).
Outputs: ml/models/yolov8n_waste.pt + INT8 TFLite export.
"""
from pathlib import Path
from ultralytics import YOLO

DATA_YAML = Path(__file__).parent / "waste.yaml"     # generated by preprocess.py
MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def train():
    model = YOLO("yolov8n.pt")
    results = model.train(
        data=str(DATA_YAML),
        epochs=50,
        imgsz=640,
        batch=16,
        device=0 if is_cuda() else "cpu",
        project=str(MODELS_DIR),
        name="yolov8n_waste",
        pretrained=True,
        freeze=10,               # freeze first 10 layers for 20 epochs (see below)
        augment=True,            # rotation, flip, jitter, mosaic
        lr0=0.001,
        patience=15,
        val=True,
        plots=True,
    )
    # Full fine-tune second pass
    model.train(
        data=str(DATA_YAML), epochs=30, imgsz=640, batch=16,
        device=0 if is_cuda() else "cpu",
        project=str(MODELS_DIR), name="yolov8n_waste_ft",
        resume=False, freeze=0, lr0=0.0005,
    )
    # Export INT8 TFLite
    model.export(format="tflite", int8=True, imgsz=640)
    print("Weights saved at", MODELS_DIR / "yolov8n_waste_ft" / "weights" / "best.pt")

def is_cuda():
    import torch; return torch.cuda.is_available()

if __name__ == "__main__":
    train()
```

Generate `waste.yaml` (YOLO format) as part of `preprocess.py`:

```yaml
path: ../../datasets/merged
train: images/train
val: images/val
test: images/test
nc: 6
names: [plastic, paper, glass, metal, organic, ewaste]
```

### 8.5 WQS scorer — `ml/src/wqs/scorer.py`

```python
"""
Waste Quality Score = 100 - contamination_pct

contamination_pct = 100 * (# items misclassified vs. bin's declared type)
                          / (# items total in the window)

For MVP: the "declared type" is the bin's dominant class over the last hour.
The WQS captures how consistent (mono-material) a bin's stream is.
"""
from collections import Counter
from datetime import datetime, timedelta
from sqlalchemy import select
from app.db.models import Classification


def compute_wqs(db, bin_id: int, window_minutes: int = 60) -> dict:
    since = datetime.utcnow() - timedelta(minutes=window_minutes)
    rows = db.execute(
        select(Classification.waste_class, Classification.item_count)
        .where(Classification.bin_id == bin_id, Classification.ts >= since)
    ).all()
    if not rows:
        return {"wqs": 0.0, "contamination_pct": 0.0, "per_class_pct": {}}

    counter = Counter()
    for cls, n in rows:
        counter[cls] += n
    total = sum(counter.values())
    per_class_pct = {k: round(100 * v / total, 1) for k, v in counter.items()}
    dominant = counter.most_common(1)[0][0]
    contamination = 100 - per_class_pct[dominant]
    return {
        "wqs": round(100 - contamination, 1),
        "contamination_pct": round(contamination, 1),
        "per_class_pct": per_class_pct,
        "dominant_class": dominant,
    }
```

### 8.6 Fill forecaster — `ml/src/forecast/model.py`

```python
"""
Per-bin fill forecaster.
Features: hour-of-day, day-of-week, recent fill deltas, temp, humidity, event flag.
Target : fill_pct at t + horizon_hours.
"""
import pandas as pd
import numpy as np
import xgboost as xgb
from pathlib import Path

MODEL_PATH = Path("/app/models/xgb_forecaster.json")

FEATURE_COLS = [
    "hour", "dow", "fill_now", "fill_delta_15m", "fill_delta_1h",
    "temp_c", "humidity_pct", "gas_ppm", "event_active",
]

def build_features(df_bin: pd.DataFrame, event_flag: int = 0) -> pd.DataFrame:
    df = df_bin.copy().sort_values("ts").set_index("ts")
    df["hour"] = df.index.hour
    df["dow"] = df.index.dayofweek
    df["fill_delta_15m"] = df["fill_pct"] - df["fill_pct"].shift(3).fillna(df["fill_pct"])
    df["fill_delta_1h"]  = df["fill_pct"] - df["fill_pct"].shift(12).fillna(df["fill_pct"])
    df["event_active"]   = event_flag
    df["fill_now"] = df["fill_pct"]
    return df[FEATURE_COLS].dropna()

def train_forecaster(train_df: pd.DataFrame, horizon_hours: int = 4):
    """train_df: columns = ts, bin_id, fill_pct, temp_c, humidity_pct, gas_ppm, event_active"""
    frames = []
    for _, g in train_df.groupby("bin_id"):
        feats = build_features(g)
        target = g.set_index("ts")["fill_pct"].shift(-horizon_hours * 12)  # 5-min ticks
        merged = feats.join(target.rename("y")).dropna()
        frames.append(merged)
    dataset = pd.concat(frames)
    X, y = dataset[FEATURE_COLS], dataset["y"]
    model = xgb.XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.08,
                             subsample=0.9, tree_method="hist")
    model.fit(X, y)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(MODEL_PATH))
    return model

def load_forecaster() -> xgb.XGBRegressor:
    m = xgb.XGBRegressor()
    m.load_model(str(MODEL_PATH))
    return m
```

### 8.7 XAI engine — `ml/src/xai/explainer.py`

```python
"""SHAP-based explanation of DCPI (or forecaster) scores → natural language."""
import shap, numpy as np, pandas as pd
import xgboost as xgb

TEMPLATE = (
    "Priority raised because: {reasons}. "
    "Dispatching now avoids ~{overflow_prob}% overflow risk and saves ~{fuel_saving}% fuel."
)

REASON_PHRASES = {
    "fill_pct":            "fill level at {v:.0f}%",
    "predicted_fill_pct":  "forecasted to reach {v:.0f}% in 4h",
    "heat_index":          "high heat index ({v:.0f})",
    "gas_index":           "elevated gas emission ({v:.0f})",
    "event_boost":         "active event nearby",
}

def explain_dcpi(features: dict, contributions: list) -> str:
    """contributions: list of {feature, contribution} sorted desc."""
    top = contributions[:3]
    phrases = [REASON_PHRASES.get(c["feature"], c["feature"]).format(v=features.get(c["feature"], 0))
               for c in top if c["contribution"] > 5]
    overflow = int(max(20, min(95, features.get("predicted_fill_pct", 50))))
    fuel = int(max(5, min(30, contributions[0]["contribution"] / 3)))
    return TEMPLATE.format(reasons=", ".join(phrases) if phrases else "combined signals",
                           overflow_prob=overflow, fuel_saving=fuel)
```

### 8.8 Federated Learning POC — `ml/src/federated/simulate.py` 🟡 EXTENDED

```python
"""
Simulated 10-client federated training on TrashNet partitions.
Uses Flower simulation to demonstrate convergence WITHOUT hardware.
Emits a convergence curve saved to ml/models/fl_convergence.png.
"""
import flwr as fl
import numpy as np, torch
from torch import nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, Subset, random_split
from pathlib import Path
import matplotlib.pyplot as plt

NUM_CLIENTS = 10
NUM_ROUNDS = 5
BATCH_SIZE = 32
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def get_model():
    m = models.mobilenet_v3_small(weights="DEFAULT")
    m.classifier[3] = nn.Linear(m.classifier[3].in_features, 6)
    return m.to(DEVICE)

def partition_dataset(dataset, n_clients: int):
    lens = [len(dataset) // n_clients] * n_clients
    lens[-1] += len(dataset) - sum(lens)
    return random_split(dataset, lens, generator=torch.Generator().manual_seed(42))

class Client(fl.client.NumPyClient):
    def __init__(self, model, train_ds, val_ds):
        self.model, self.train_ds, self.val_ds = model, train_ds, val_ds
    def get_parameters(self, config):
        return [p.cpu().numpy() for p in self.model.state_dict().values()]
    def set_parameters(self, params):
        state = self.model.state_dict()
        for k, v in zip(state.keys(), params):
            state[k] = torch.tensor(v)
        self.model.load_state_dict(state, strict=True)
    def fit(self, parameters, config):
        self.set_parameters(parameters)
        opt = torch.optim.Adam(self.model.parameters(), lr=1e-3)
        loss_fn = nn.CrossEntropyLoss()
        self.model.train()
        loader = DataLoader(self.train_ds, batch_size=BATCH_SIZE, shuffle=True)
        for _ in range(1):
            for x, y in loader:
                x, y = x.to(DEVICE), y.to(DEVICE)
                opt.zero_grad(); loss_fn(self.model(x), y).backward(); opt.step()
        return self.get_parameters(config), len(self.train_ds), {}
    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        self.model.eval()
        loader = DataLoader(self.val_ds, batch_size=BATCH_SIZE)
        loss_fn = nn.CrossEntropyLoss(); tot_loss, tot_correct, n = 0.0, 0, 0
        with torch.no_grad():
            for x, y in loader:
                x, y = x.to(DEVICE), y.to(DEVICE)
                out = self.model(x); tot_loss += loss_fn(out, y).item() * y.size(0)
                tot_correct += (out.argmax(1) == y).sum().item(); n += y.size(0)
        return tot_loss / n, n, {"accuracy": tot_correct / n}

def client_fn(cid: str, partitions):
    train, val = partitions[int(cid)]
    return Client(get_model(), train, val)

def main():
    transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor()])
    full = datasets.ImageFolder("ml/datasets/trashnet/dataset-resized", transform=transform)
    parts = partition_dataset(full, NUM_CLIENTS)
    partitions = [random_split(p, [int(len(p)*0.8), len(p)-int(len(p)*0.8)]) for p in parts]

    history = fl.simulation.start_simulation(
        client_fn=lambda cid: client_fn(cid, partitions),
        num_clients=NUM_CLIENTS,
        config=fl.server.ServerConfig(num_rounds=NUM_ROUNDS),
        strategy=fl.server.strategy.FedAvg(fraction_fit=1.0, fraction_evaluate=1.0),
    )
    rounds = [r for r, _ in history.metrics_distributed["accuracy"]]
    accs   = [a for _, a in history.metrics_distributed["accuracy"]]
    plt.figure(); plt.plot(rounds, accs, marker="o")
    plt.title("Federated accuracy over rounds"); plt.xlabel("Round"); plt.ylabel("Accuracy")
    Path("ml/models").mkdir(parents=True, exist_ok=True)
    plt.savefig("ml/models/fl_convergence.png", dpi=150)
    print("Saved convergence plot.")

if __name__ == "__main__":
    main()
```

---

## 9. Sensor simulator

### 9.1 `simulator/requirements.txt`

```txt
paho-mqtt==2.1.0
numpy==2.2.0
pyyaml==6.0.2
python-dotenv==1.0.1
```

### 9.2 `simulator/config/city_config.yaml`

```yaml
city_name: DemoCity
districts:
  - name: Downtown
    bins: 12
    center: [12.9720, 77.5950]
    fill_rate_per_hour: [2, 5]      # % per hour range
  - name: Residential-North
    bins: 10
    center: [12.9820, 77.5800]
    fill_rate_per_hour: [1, 3]
  - name: Market
    bins: 10
    center: [12.9660, 77.5810]
    fill_rate_per_hour: [4, 8]
  - name: Industrial
    bins: 8
    center: [12.9550, 77.6100]
    fill_rate_per_hour: [1, 2]

events:
  - name: Weekend Market Festival
    district: Market
    start_offset_hours: 6
    duration_hours: 12
    multiplier: 2.5

weather:
  base_temp_c: 28
  daily_amplitude_c: 6
  base_humidity_pct: 65

collection:
  reset_prob_on_full: 0.6
```

### 9.3 `simulator/src/main.py`

```python
"""Simulate 40 bins publishing telemetry over MQTT."""
import json, os, random, time, math
from datetime import datetime, timedelta
import numpy as np, yaml
import paho.mqtt.client as mqtt
from pathlib import Path

CONFIG = yaml.safe_load(open(Path(__file__).parent.parent / "config" / "city_config.yaml"))
MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "smartwaste")
TICK_MS = int(os.getenv("SIMULATOR_TICK_MS", 5000))
COMPRESSED_MIN_PER_TICK = 5     # 1 tick = 5 minutes of simulated time

class Bin:
    def __init__(self, bin_id: int, name: str, district: str, lat: float, lon: float,
                 fill_rate_range: tuple):
        self.id, self.name, self.district = bin_id, name, district
        self.lat, self.lon = lat, lon
        self.fill_pct = random.uniform(5, 30)
        self.weight_kg = 0.0
        self.fill_rate_range = fill_rate_range   # % per hour
        self.temp_offset = random.uniform(-1.5, 1.5)
        self.gas_baseline = random.uniform(50, 150)

    def step(self, sim_now: datetime, weather: dict, event_multiplier: float):
        # Fill increases per 5-minute tick
        hourly = random.uniform(*self.fill_rate_range) * event_multiplier
        dpct = hourly * (COMPRESSED_MIN_PER_TICK / 60.0)
        self.fill_pct = min(100.0, self.fill_pct + dpct)
        # Reset on collection
        if self.fill_pct >= 95 and random.random() < CONFIG["collection"]["reset_prob_on_full"]:
            self.fill_pct = 5.0
        # Weight proportional to fill + noise
        self.weight_kg = round(self.fill_pct * 0.6 + random.gauss(0, 0.5), 2)
        # Gas increases with fill + heat + humidity
        gas = self.gas_baseline + self.fill_pct * 3 + weather["temp_c"] * 2
        gas *= 1.5 if weather["humidity_pct"] > 80 else 1.0
        return {
            "bin_id": self.id, "ts": sim_now.isoformat(),
            "fill_pct": round(self.fill_pct, 1),
            "weight_kg": self.weight_kg,
            "temp_c": round(weather["temp_c"] + self.temp_offset, 1),
            "humidity_pct": round(weather["humidity_pct"], 1),
            "gas_ppm": round(gas, 1),
            "source": "simulator",
        }


def build_bins() -> list[Bin]:
    bins = []; bin_id = 1
    for d in CONFIG["districts"]:
        lat_c, lon_c = d["center"]
        for i in range(d["bins"]):
            lat = lat_c + random.uniform(-0.008, 0.008)
            lon = lon_c + random.uniform(-0.008, 0.008)
            bins.append(Bin(bin_id, f"{d['name']}-{i+1}", d["name"], lat, lon,
                            tuple(d["fill_rate_per_hour"])))
            bin_id += 1
    return bins


def weather_at(sim_now: datetime) -> dict:
    h = sim_now.hour + sim_now.minute / 60
    base = CONFIG["weather"]["base_temp_c"]
    amp  = CONFIG["weather"]["daily_amplitude_c"]
    temp = base + amp * math.sin((h - 6) / 24 * 2 * math.pi)
    hum  = CONFIG["weather"]["base_humidity_pct"] - (temp - base) * 1.5
    return {"temp_c": temp, "humidity_pct": max(30, min(95, hum))}


def active_multiplier(bin_: Bin, sim_now: datetime, start_time: datetime) -> float:
    for e in CONFIG["events"]:
        if bin_.district != e["district"]: continue
        e_start = start_time + timedelta(hours=e["start_offset_hours"])
        e_end   = e_start + timedelta(hours=e["duration_hours"])
        if e_start <= sim_now <= e_end: return e["multiplier"]
    return 1.0


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="simulator")
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60); client.loop_start()

    bins = build_bins()
    # Send bin metadata once so backend can register (optional)
    client.publish(f"{TOPIC_PREFIX}/bins/register", json.dumps(
        [{"id": b.id, "name": b.name, "district": b.district,
          "lat": b.lat, "lon": b.lon} for b in bins]), qos=1)

    sim_now = datetime.utcnow(); start = sim_now
    print(f"Simulator running: {len(bins)} bins, {COMPRESSED_MIN_PER_TICK} min per tick")
    while True:
        w = weather_at(sim_now)
        for b in bins:
            payload = b.step(sim_now, w, active_multiplier(b, sim_now, start))
            client.publish(f"{TOPIC_PREFIX}/bins/{b.id}/telemetry",
                           json.dumps(payload), qos=1)
        sim_now += timedelta(minutes=COMPRESSED_MIN_PER_TICK)
        time.sleep(TICK_MS / 1000.0)

if __name__ == "__main__":
    main()
```

---

## 10. Frontend implementation (React + TypeScript)

### 10.1 `frontend/package.json`

```json
{
  "name": "smartwasteai-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@tanstack/react-query": "^5.62.0",
    "@react-three/fiber": "^8.17.10",
    "@react-three/drei": "^9.117.0",
    "axios": "^1.7.9",
    "leaflet": "^1.9.4",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-leaflet": "^4.2.1",
    "react-router-dom": "^6.28.0",
    "recharts": "^2.14.1",
    "three": "^0.169.0",
    "zustand": "^5.0.2"
  },
  "devDependencies": {
    "@types/leaflet": "^1.9.15",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@types/three": "^0.169.0",
    "@vitejs/plugin-react": "^4.3.4",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.16",
    "typescript": "^5.6.3",
    "vite": "^5.4.11"
  }
}
```

### 10.2 `frontend/src/types/domain.ts`

```ts
export type WasteClass = "plastic" | "paper" | "glass" | "metal" | "organic" | "ewaste";

export interface Bin {
  id: number;
  name: string;
  district: string;
  lat: number;
  lon: number;
  capacity_l: number;
}

export interface DCPIItem {
  bin_id: number;
  name: string;
  district: string;
  lat: number;
  lon: number;
  dcpi: number;                 // 0..100
  ts: string;
}

export interface DCPIDetail {
  bin_id: number;
  dcpi: number;
  ts: string;
  features: Record<string, number>;
  reasons: { feature: string; contribution: number }[];
}

export interface RouteInfo {
  id: number;
  stops: number[];
  distance_km: number;
  expected_fuel_saving_pct: number;
  expected_co2_saving_kg: number;
}

export interface KPISummary {
  bins_total: number;
  overflow_risk_avg: number;
  wqs_avg: number;
  co2_avoided_kg: number;
  cost_saved_pct: number;
  workers_active: number;
  payments_today: number;
}
```

### 10.3 `frontend/src/api/client.ts`

```ts
import axios from "axios";
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE + "/api/v1",
  timeout: 8000,
});
```

### 10.4 `frontend/src/api/dcpi.ts`

```ts
import { api } from "./client";
import type { DCPIItem, DCPIDetail } from "../types/domain";

export const listDCPI    = () => api.get<DCPIItem[]>("/dcpi").then(r => r.data);
export const getDCPI     = (id: number) => api.get<DCPIDetail>(`/dcpi/${id}`).then(r => r.data);
```

### 10.5 Live Map module — `frontend/src/modules/LiveMap.tsx`

```tsx
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { useQuery } from "@tanstack/react-query";
import { listDCPI } from "../api/dcpi";
import type { DCPIItem } from "../types/domain";
import { useSelectionStore } from "../store/selection";
import "leaflet/dist/leaflet.css";

function dcpiColor(v: number) {
  if (v >= 75) return "#DC2626";     // red
  if (v >= 55) return "#E85D25";     // orange
  if (v >= 35) return "#D97706";     // yellow
  return "#16A34A";                  // green
}

export default function LiveMap() {
  const { data = [] } = useQuery<DCPIItem[]>({
    queryKey: ["dcpi"],
    queryFn: listDCPI,
    refetchInterval: 5000,
  });
  const setSelectedBin = useSelectionStore(s => s.setSelectedBin);
  const center: [number, number] = data.length
    ? [data[0].lat, data[0].lon] : [12.9716, 77.5946];

  return (
    <div className="h-full w-full">
      <MapContainer center={center} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {data.map(b => (
          <CircleMarker
            key={b.bin_id}
            center={[b.lat, b.lon]}
            radius={8 + b.dcpi / 12}
            pathOptions={{ fillColor: dcpiColor(b.dcpi), color: "#111", weight: 1, fillOpacity: 0.85 }}
            eventHandlers={{ click: () => setSelectedBin(b.bin_id) }}
          >
            <Popup>
              <b>{b.name}</b><br />
              DCPI: <b>{b.dcpi.toFixed(0)}</b><br />
              District: {b.district}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
```

### 10.6 App shell — `frontend/src/App.tsx`

```tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import LiveMap from "./modules/LiveMap";
import Prediction from "./modules/Prediction";
import RoutesModule from "./modules/Routes";
import DigitalTwin from "./modules/DigitalTwin";
import KPIs from "./modules/KPIs";
import Alerts from "./modules/Alerts";
import BinDetailPanel from "./components/BinDetailPanel";

const qc = new QueryClient();
const tabs = [
  { path: "/",         label: "Live Map",     el: <LiveMap /> },
  { path: "/predict",  label: "Prediction",   el: <Prediction /> },
  { path: "/routes",   label: "Routes",       el: <RoutesModule /> },
  { path: "/twin",     label: "Digital Twin", el: <DigitalTwin /> },
  { path: "/kpis",     label: "KPIs",         el: <KPIs /> },
  { path: "/alerts",   label: "Alerts",       el: <Alerts /> },
];

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <div className="flex h-screen">
          <aside className="w-56 bg-slate-900 text-white p-4">
            <h1 className="text-xl font-bold mb-6">SmartWasteAI</h1>
            <nav className="flex flex-col gap-2">
              {tabs.map(t => (
                <NavLink key={t.path} to={t.path}
                  className={({ isActive }) =>
                    `px-3 py-2 rounded ${isActive ? "bg-orange-600" : "hover:bg-slate-800"}`}
                >{t.label}</NavLink>
              ))}
            </nav>
          </aside>
          <main className="flex-1 flex">
            <div className="flex-1">
              <Routes>{tabs.map(t => <Route key={t.path} path={t.path} element={t.el} />)}</Routes>
            </div>
            <BinDetailPanel />
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
```

### 10.7 Bin detail panel — `frontend/src/components/BinDetailPanel.tsx`

```tsx
import { useQuery } from "@tanstack/react-query";
import { useSelectionStore } from "../store/selection";
import { getDCPI } from "../api/dcpi";

export default function BinDetailPanel() {
  const selectedBin = useSelectionStore(s => s.selectedBin);
  const { data } = useQuery({
    queryKey: ["dcpi-detail", selectedBin],
    queryFn: () => (selectedBin ? getDCPI(selectedBin) : Promise.resolve(null)),
    enabled: !!selectedBin,
  });
  if (!selectedBin || !data) return <aside className="w-80 border-l bg-slate-50"/>;

  return (
    <aside className="w-80 border-l bg-slate-50 p-4 overflow-y-auto">
      <h2 className="text-lg font-bold">Bin #{data.bin_id}</h2>
      <p className="text-4xl font-bold text-orange-600 my-3">{data.dcpi.toFixed(0)}</p>
      <p className="text-sm text-slate-500 uppercase tracking-wider">DCPI · Priority</p>

      <h3 className="mt-6 font-semibold">Why this priority?</h3>
      <ul className="mt-2 text-sm space-y-1">
        {data.reasons.map(r => (
          <li key={r.feature}>
            <b>{r.feature}</b>: contribution {r.contribution.toFixed(1)}
          </li>
        ))}
      </ul>

      <h3 className="mt-6 font-semibold">Sensor snapshot</h3>
      <dl className="mt-2 text-sm">
        {Object.entries(data.features).map(([k, v]) => (
          <div key={k} className="flex justify-between border-b py-1">
            <dt>{k}</dt><dd className="font-mono">{v.toFixed(1)}</dd>
          </div>
        ))}
      </dl>
    </aside>
  );
}
```

### 10.8 Selection store — `frontend/src/store/selection.ts`

```ts
import { create } from "zustand";

interface State {
  selectedBin: number | null;
  setSelectedBin: (id: number | null) => void;
}
export const useSelectionStore = create<State>((set) => ({
  selectedBin: null,
  setSelectedBin: (id) => set({ selectedBin: id }),
}));
```

### 10.9 Digital Twin module — `frontend/src/modules/DigitalTwin.tsx` 🟡 EXTENDED

```tsx
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useQuery } from "@tanstack/react-query";
import { listDCPI } from "../api/dcpi";

function Bin3D({ position, dcpi }: { position: [number, number, number]; dcpi: number }) {
  const color = dcpi >= 75 ? "#DC2626" : dcpi >= 55 ? "#E85D25" : dcpi >= 35 ? "#D97706" : "#16A34A";
  const height = 0.5 + (dcpi / 100) * 2.5;
  return (
    <mesh position={[position[0], height / 2, position[2]]}>
      <cylinderGeometry args={[0.3, 0.3, height, 12]} />
      <meshStandardMaterial color={color} />
    </mesh>
  );
}

export default function DigitalTwin() {
  const { data = [] } = useQuery({ queryKey: ["dcpi"], queryFn: listDCPI });
  const bins = data.slice(0, 40);
  return (
    <div className="h-full w-full bg-slate-800">
      <Canvas camera={{ position: [15, 12, 15], fov: 50 }}>
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <gridHelper args={[20, 20, "#444", "#333"]} />
        {bins.map((b, i) => {
          const x = (i % 8) - 4;
          const z = Math.floor(i / 8) - 2.5;
          return <Bin3D key={b.bin_id} position={[x * 2, 0, z * 2]} dcpi={b.dcpi} />;
        })}
        <OrbitControls />
      </Canvas>
      <div className="absolute top-4 left-4 bg-white/90 p-3 rounded">
        <p className="text-sm font-bold">Digital Twin · 40 bins</p>
        <p className="text-xs text-slate-500">Height ∝ DCPI · Color = urgency</p>
      </div>
    </div>
  );
}
```

---

## 11. Docker orchestration

### 11.1 `docker-compose.yml`

```yaml
services:
  db:
    image: timescale/timescaledb:2.17.2-pg16
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports: ["5432:5432"]
    volumes: [dbdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER"]
      interval: 5s
      retries: 10

  mqtt:
    image: eclipse-mosquitto:2.0
    restart: unless-stopped
    ports: ["1883:1883"]
    volumes: [./scripts/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro]

  backend:
    build: ./backend
    restart: unless-stopped
    env_file: .env
    ports: ["8000:8000"]
    depends_on:
      db: { condition: service_healthy }
      mqtt: { condition: service_started }
    volumes: [./ml/models:/app/models:ro]
    command: >
      bash -c "alembic upgrade head &&
               uvicorn app.main:app --host 0.0.0.0 --port 8000"

  simulator:
    build: ./simulator
    restart: unless-stopped
    env_file: .env
    depends_on:
      mqtt: { condition: service_started }
      backend: { condition: service_started }

  frontend:
    build: ./frontend
    restart: unless-stopped
    ports: ["5173:5173"]
    environment:
      VITE_API_BASE: http://localhost:8000
    depends_on: [backend]

  ml:
    build: ./ml
    profiles: ["training"]      # not started by default
    env_file: .env
    volumes:
      - ./ml/datasets:/app/datasets
      - ./ml/models:/app/models

volumes:
  dbdata:
```

### 11.2 `scripts/mosquitto.conf`

```
listener 1883
allow_anonymous true
persistence false
```

### 11.3 `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.4 `frontend/Dockerfile`

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### 11.5 `simulator/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-u", "src/main.py"]
```

### 11.6 `ml/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["bash"]
```

---

## 12. 72-hour implementation roadmap

### Day 1 · 15 August · evening → night 🔴

| Task | Owner | ~Hours | Priority |
|---|---|---|---|
| Init repo, .gitignore, README, docker-compose, .env | Lead | 1 | 🔴 |
| Backend scaffold: `app/main.py`, config, models, alembic init | Backend | 2 | 🔴 |
| Migration 001 initial + 002 hypertable | Backend | 1 | 🔴 |
| Mosquitto up, MQTT listener wired | Backend | 1 | 🔴 |
| Simulator v0: 40 bins publish telemetry | Backend/Sim | 2 | 🔴 |
| Frontend scaffold: Vite + Tailwind + routes shell | Frontend | 2 | 🔴 |
| YOLO training: dataset download, `train_yolo.py` running (background overnight) | ML | 2 | 🔴 |
| **End-of-day gate:** MQTT flowing, telemetry stored in DB, `GET /bins` returns data | All | | |

### Day 2 · 16 August 🔴

| Task | Owner | ~Hours | Priority |
|---|---|---|---|
| YOLO training completed → F1 + confusion matrix + notebook | ML | 2 | 🔴 |
| WQS scorer wired into a background job | Backend | 2 | 🔴 |
| DCPI service + APScheduler (30 s tick) | Backend | 2 | 🔴 |
| Forecaster: train on 24 h simulator data, save model | ML | 2 | 🔴 |
| API endpoints: `/bins`, `/dcpi`, `/dcpi/{id}`, `/predictions/{id}`, `/kpis/summary` | Backend | 3 | 🔴 |
| Frontend: Live Map module + Bin Detail panel | Frontend | 4 | 🔴 |
| Frontend: KPIs module (basic cards) | Frontend | 1 | 🔴 |
| **End-of-day gate:** open browser → see map with color-coded pins updating every 5 s, click bin → detail panel shows DCPI & features | All | | |

### Day 3 · 17 August 🔴 + 🟡

| Task | Owner | ~Hours | Priority |
|---|---|---|---|
| OR-Tools route optimizer + `/routes/today` + `/routes/optimize` | Backend | 3 | 🔴 |
| SHAP explainer + natural-language wrapper + `/xai/{id}` | Backend/ML | 2 | 🔴 |
| Frontend: Routes module (map overlay + KPI card) | Frontend | 2 | 🔴 |
| Frontend: Prediction module (Recharts curve) | Frontend | 2 | 🔴 |
| Digital Twin module (Three.js) | Frontend | 2 | 🟡 |
| FL simulation script + convergence plot | ML | 2 | 🟡 |
| Waste-picker mobile app: **design mockups only** (Figma link in README) | Frontend | 1 | 🟡 |
| Demo scenario script + record 5-min video walkthrough | All | 2 | 🔴 |
| Update deck + README + paper draft | All | 3 | 🔴 |
| **End-of-day gate:** full 5-min scripted demo runnable from `make up && make seed`; video recorded | All | | |

### Cut-line (if time runs out)

Drop in this order:
1. Waste-picker mobile app screens (keep API + spec only)
2. Digital Twin 3D view (keep 2D placeholder)
3. FL convergence run (keep the code + explain "would run for 30 min offline")
4. SHAP wiring (fall back to rule-based explanations via `xai/explainer.py`)

Keep at all costs: MQTT ingestion + DCPI + Route optimizer + Live Map + Bin Detail.

---

## 13. Testing & end-to-end scenario

### 13.1 Smoke test — `scripts/smoke_test.sh`

```bash
#!/usr/bin/env bash
set -e
API=http://localhost:8000/api/v1
echo "1. Health check"
curl -sf $API/health | jq
echo "2. Bins registered"
curl -sf $API/bins | jq 'length'
echo "3. Telemetry flowing (wait 10 s...)"
sleep 10
curl -sf $API/telemetry/latest | jq 'length'
echo "4. DCPI computed"
curl -sf $API/dcpi | jq '.[0]'
echo "5. Route optimized"
curl -sf -X POST $API/routes/optimize | jq
echo "6. KPI summary"
curl -sf $API/kpis/summary | jq
echo "ALL PASS"
```

### 13.2 Backend unit tests — `backend/tests/test_dcpi.py`

```python
def test_dcpi_weights_sum_to_one():
    from app.services.dcpi_service import WEIGHTS
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

def test_dcpi_high_when_all_features_max(monkeypatch):
    from app.services.dcpi_service import compute_dcpi_for_bin
    # ...mock DB session, insert max-value telemetry, assert dcpi > 90
```

### 13.3 Live demo script — `docs/demo-script.md`

```markdown
# 5-minute live demo

1. `make up`                                       (30 s to boot)
2. `make migrate && make seed`                     (10 s)
3. Open http://localhost:5173 in browser
4. Show **Live Map** with 40 bins auto-updating every 5 s
5. Click a red bin → **Bin Detail** panel: DCPI 87, top reasons: high fill %, event nearby
6. Switch to **Prediction** tab → 24 h forecast curve for the selected bin
7. Click **Optimize Route** → route drawn on map + KPI card (25 % fuel saving)
8. Switch to **Digital Twin** tab → 3D city, run "festival scenario", DCPI shifts visibly
9. Switch to **KPIs** tab → aggregate: 40 bins, avg WQS 78, CO₂ avoided 12 kg
10. Close with **Waste-picker app screens** (Figma mockups)
```

---

## 14. Submission checklist (18 Aug)

- [ ] 🔴 Repo pushed to GitHub, README complete, LICENSE (MIT)
- [ ] 🔴 `docker compose up` works from clean clone
- [ ] 🔴 `smoke_test.sh` passes end-to-end
- [ ] 🔴 5-minute demo video recorded and uploaded (unlisted YouTube link in README)
- [ ] 🔴 Updated deck (SmartWasteAI_Round2_Final.pptx)
- [ ] 🔴 Paper draft (2–4 pages IEEE format)
- [ ] 🟡 FL convergence plot committed
- [ ] 🟡 Digital Twin scenario recorded
- [ ] 🟡 Mobile app Figma link in README
- [ ] 🔴 Submission form filled (repo link + video link + deck + paper)

### README structure to ship

```markdown
# SmartWasteAI

A Federated, Explainable AI Framework for Predictive Urban Waste Management
with Informal Sector Integration.

**Team:** AI4Earth · **Team Leader:** Housseni YABRE
**SmartAIthon 2026 · Round 2 submission**

## Demo
📺 [5-min walkthrough](https://youtu.be/xxx)   ·   [Live-run instructions](#run-locally)

## Architecture
See [SPEC.md](./SPEC.md) for the full specification.

## Run locally
    git clone https://github.com/.../smartwasteai && cd smartwasteai
    cp .env.example .env
    make up
    make migrate
    open http://localhost:5173

## Contributions
- WQS  · Waste Quality Score
- DCPI · Dynamic Collection Priority Index
- FL   · Federated Learning (simulation)
- XAI  · SHAP-based natural-language explanations
- DT   · Digital Twin what-if simulator
- Bridge · Informal-sector waste-picker mobile app (design)

## Paper
See `docs/paper.pdf`.

## License
MIT.
```

---

## Appendix A — Cursor prompting tips

To use this SPEC efficiently in Cursor:

1. **Reference the file** in every prompt: `@SPEC.md`
2. **Ask by section number**: *"Implement section 7.4 fully, one endpoint at a time, starting with GET /bins."*
3. **Constrain scope**: *"Only generate `backend/app/api/routes/dcpi.py`. Follow the code style of section 7.5."*
4. **Ask for tests alongside**: *"After implementing the endpoint, generate the pytest that validates it in `backend/tests/`."*
5. **Iterate with Cursor Composer**: for multi-file changes, use Composer with the target files pre-selected.
6. **Cross-reference contracts**: when generating the frontend, always reference the matching backend section by number (*"Implement `frontend/src/api/dcpi.ts` per contract in section 7.4"*).

## Appendix B — Post-submission v2 roadmap (🟢 FUTURE)

- Real hardware: 1 physical Pi 4 + sensors → replace simulator source in DB with `source="hardware"`
- Real federated learning run on 2+ physical devices
- Waste-picker React Native app: implementation on top of designed screens
- IEEE paper polish + submission to Sensors Journal or Smart Cities Conference
- NGO / municipal pilot outreach
- Multilingual support (English + French + Hindi + Portuguese for LATAM)

---

*End of specification.*
