from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Bin, Collection, DCPIScore, Route, Worker, WQSScore
from app.db.schemas import KPISummary

router = APIRouter(prefix="/api/v1/kpis", tags=["kpis"])


@router.get("/summary", response_model=KPISummary)
def kpi_summary(db: Session = Depends(get_db)):
    bins_total = db.execute(select(func.count(Bin.id))).scalar() or 0

    wqs_sub = (
        select(WQSScore.bin_id, func.max(WQSScore.ts).label("max_ts"))
        .group_by(WQSScore.bin_id)
        .subquery()
    )
    wqs_rows = db.execute(
        select(WQSScore.wqs)
        .join(wqs_sub, (WQSScore.bin_id == wqs_sub.c.bin_id) & (WQSScore.ts == wqs_sub.c.max_ts))
    ).scalars().all()
    wqs_avg = round(sum(wqs_rows) / len(wqs_rows), 1) if wqs_rows else 72.0

    dcpi_sub = (
        select(DCPIScore.bin_id, func.max(DCPIScore.ts).label("max_ts"))
        .group_by(DCPIScore.bin_id)
        .subquery()
    )
    dcpi_rows = db.execute(
        select(DCPIScore.dcpi)
        .join(dcpi_sub, (DCPIScore.bin_id == dcpi_sub.c.bin_id) & (DCPIScore.ts == dcpi_sub.c.max_ts))
    ).scalars().all()
    overflow_risk_avg = round(sum(dcpi_rows) / len(dcpi_rows), 1) if dcpi_rows else 0.0

    route = db.execute(select(Route).order_by(desc(Route.ts)).limit(1)).scalar_one_or_none()
    co2_avoided = route.expected_co2_saving_kg if route else 0.0
    cost_saved_pct = route.expected_fuel_saving_pct if route else 0.0

    workers_active = db.execute(
        select(func.count(Worker.id)).where(Worker.active.is_(True))
    ).scalar() or 0

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    payments = db.execute(
        select(func.coalesce(func.sum(Collection.payment_amount), 0)).where(
            Collection.ts >= today_start
        )
    ).scalar() or 0

    return KPISummary(
        bins_total=bins_total,
        overflow_risk_avg=overflow_risk_avg,
        wqs_avg=wqs_avg,
        co2_avoided_kg=co2_avoided,
        cost_saved_pct=cost_saved_pct,
        workers_active=workers_active,
        payments_today=float(payments),
    )
