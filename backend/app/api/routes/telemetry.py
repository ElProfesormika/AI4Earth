from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Bin, Telemetry
from app.db.schemas import TelemetryLatest, TelemetryOut

router = APIRouter(prefix="/api/v1", tags=["telemetry"])


@router.get("/bins/{bin_id}/telemetry", response_model=list[TelemetryOut])
def bin_telemetry(
    bin_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    if not db.get(Bin, bin_id):
        raise HTTPException(404, "bin not found")
    rows = (
        db.execute(
            select(Telemetry)
            .where(Telemetry.bin_id == bin_id)
            .order_by(desc(Telemetry.ts))
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return list(reversed(rows))


@router.get("/telemetry/latest", response_model=list[TelemetryLatest])
def telemetry_latest(db: Session = Depends(get_db)):
    sub = (
        select(
            Telemetry.bin_id,
            func.max(Telemetry.ts).label("max_ts"),
        )
        .group_by(Telemetry.bin_id)
        .subquery()
    )
    rows = db.execute(
        select(Telemetry, Bin.name, Bin.district)
        .join(sub, (Telemetry.bin_id == sub.c.bin_id) & (Telemetry.ts == sub.c.max_ts))
        .join(Bin, Bin.id == Telemetry.bin_id)
        .order_by(Telemetry.bin_id)
    ).all()

    return [
        TelemetryLatest(
            ts=t.ts,
            bin_id=t.bin_id,
            fill_pct=t.fill_pct,
            weight_kg=t.weight_kg,
            temp_c=t.temp_c,
            humidity_pct=t.humidity_pct,
            gas_ppm=t.gas_ppm,
            source=t.source,
            bin_name=name,
            district=district,
        )
        for t, name, district in rows
    ]
