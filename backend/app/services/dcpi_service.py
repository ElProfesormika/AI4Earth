"""
DCPI = w_fill * fill_pct
     + w_pred * predicted_fill_pct
     + w_temp * heat_index
     + w_gas  * gas_index
     + w_evt  * event_boost
"""
from datetime import datetime, timedelta

from sqlalchemy import desc, select

from app.db.models import Bin, CityEvent, DCPIScore, Prediction, Telemetry
from app.db.session import SessionLocal

WEIGHTS = {"fill": 0.35, "pred": 0.25, "temp": 0.10, "gas": 0.15, "event": 0.15}

WEIGHT_KEY = {
    "fill_pct": "fill",
    "predicted_fill_pct": "pred",
    "heat_index": "temp",
    "gas_index": "gas",
    "event_boost": "event",
}


def compute_dcpi_for_bin(bin_id: int, db) -> tuple[float, dict, list]:
    now = datetime.utcnow()
    latest_tel = db.execute(
        select(Telemetry).where(Telemetry.bin_id == bin_id).order_by(desc(Telemetry.ts)).limit(1)
    ).scalar_one_or_none()
    if not latest_tel:
        return 0.0, {}, []

    latest_pred = db.execute(
        select(Prediction)
        .where(
            Prediction.bin_id == bin_id,
            Prediction.ts_target > now,
            Prediction.ts_target < now + timedelta(hours=4),
        )
        .order_by(desc(Prediction.ts_target))
        .limit(1)
    ).scalar_one_or_none()

    bin_ = db.get(Bin, bin_id)
    active_event = db.execute(
        select(CityEvent)
        .where(
            CityEvent.district == bin_.district,
            CityEvent.start_ts <= now,
            CityEvent.end_ts >= now,
        )
        .limit(1)
    ).scalar_one_or_none()

    fill = latest_tel.fill_pct
    pred = latest_pred.predicted_fill_pct if latest_pred else fill
    heat = min(100.0, max(0.0, (latest_tel.temp_c - 20) * 5))
    gas = min(100.0, latest_tel.gas_ppm / 10.0)
    evt = 100.0 if active_event else 0.0

    features = {
        "fill_pct": fill,
        "predicted_fill_pct": pred,
        "heat_index": heat,
        "gas_index": gas,
        "event_boost": evt,
    }
    dcpi = (
        WEIGHTS["fill"] * fill
        + WEIGHTS["pred"] * pred
        + WEIGHTS["temp"] * heat
        + WEIGHTS["gas"] * gas
        + WEIGHTS["event"] * evt
    )

    contributions = sorted(
        [
            (k, WEIGHTS[WEIGHT_KEY[k]] * v)
            for k, v in features.items()
        ],
        key=lambda x: -x[1],
    )
    reasons = [{"feature": k, "contribution": round(v, 2)} for k, v in contributions[:3]]
    return round(dcpi, 2), features, reasons


def recompute_all_dcpi():
    with SessionLocal() as db:
        bin_ids = [b.id for b in db.execute(select(Bin)).scalars()]
        for bid in bin_ids:
            score, feats, reasons = compute_dcpi_for_bin(bid, db)
            db.add(
                DCPIScore(
                    bin_id=bid,
                    ts=datetime.utcnow(),
                    dcpi=score,
                    features=feats,
                    reasons=reasons,
                )
            )
        db.commit()
