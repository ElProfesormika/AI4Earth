from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import desc, select

from app.config import settings
from app.db.models import Bin, CityEvent, Prediction, Telemetry
from app.db.session import SessionLocal

FEATURE_COLS = [
    "hour",
    "dow",
    "fill_now",
    "fill_delta_15m",
    "fill_delta_1h",
    "temp_c",
    "humidity_pct",
    "gas_ppm",
    "event_active",
]


def _model_path() -> Path:
    return Path(settings.forecast_model)


def _load_model():
    import xgboost as xgb

    path = _model_path()
    if path.exists():
        model = xgb.XGBRegressor()
        model.load_model(str(path))
        return model
    return None


def _rule_based_forecast(fill_now: float, hourly_rate: float, steps: int) -> list[float]:
    values = []
    current = fill_now
    for _ in range(steps):
        current = min(100.0, current + hourly_rate / 12)
        values.append(round(current, 1))
    return values


def _build_features_row(tel: Telemetry, event_active: int = 0) -> dict:
    ts = tel.ts
    return {
        "hour": ts.hour,
        "dow": ts.weekday(),
        "fill_now": tel.fill_pct,
        "fill_delta_15m": 0.5,
        "fill_delta_1h": 1.5,
        "temp_c": tel.temp_c,
        "humidity_pct": tel.humidity_pct,
        "gas_ppm": tel.gas_ppm,
        "event_active": event_active,
    }


def forecast_bin(db, bin_id: int, horizon_hours: int = 24) -> list[Prediction]:
    now = datetime.utcnow()
    tel = db.execute(
        select(Telemetry).where(Telemetry.bin_id == bin_id).order_by(desc(Telemetry.ts)).limit(1)
    ).scalar_one_or_none()
    if not tel:
        return []

    bin_ = db.get(Bin, bin_id)
    event = db.execute(
        select(CityEvent)
        .where(
            CityEvent.district == bin_.district,
            CityEvent.start_ts <= now,
            CityEvent.end_ts >= now,
        )
        .limit(1)
    ).scalar_one_or_none()
    event_active = 1 if event else 0

    model = _load_model()
    predictions: list[Prediction] = []
    tick_minutes = 5
    steps = horizon_hours * (60 // tick_minutes)

    if model:
        row = _build_features_row(tel, event_active)
        x = pd.DataFrame([row])[FEATURE_COLS]
        for i in range(1, steps + 1):
            pred_fill = float(np.clip(model.predict(x)[0], 0, 100))
            ts_target = now + timedelta(minutes=i * tick_minutes)
            p = Prediction(
                bin_id=bin_id,
                ts_made=now,
                ts_target=ts_target,
                predicted_fill_pct=round(pred_fill, 1),
                horizon_hours=horizon_hours,
            )
            predictions.append(p)
            db.add(p)
            row["fill_now"] = pred_fill
            x = pd.DataFrame([row])[FEATURE_COLS]
    else:
        fills = _rule_based_forecast(tel.fill_pct, 2.0 * (1.5 if event_active else 1.0), steps)
        for i, fill in enumerate(fills, start=1):
            ts_target = now + timedelta(minutes=i * tick_minutes)
            p = Prediction(
                bin_id=bin_id,
                ts_made=now,
                ts_target=ts_target,
                predicted_fill_pct=fill,
                horizon_hours=horizon_hours,
            )
            predictions.append(p)
            db.add(p)

    return predictions


def recompute_forecasts():
    with SessionLocal() as db:
        bin_ids = [b.id for b in db.execute(select(Bin)).scalars()]
        for bid in bin_ids:
            forecast_bin(db, bid, horizon_hours=4)
        db.commit()
