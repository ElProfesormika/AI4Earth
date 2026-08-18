from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Bin, Prediction
from app.db.schemas import PredictionCurve, PredictionPoint

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])


@router.get("/{bin_id}", response_model=PredictionCurve)
def get_predictions(
    bin_id: int,
    horizon: int = Query(24, ge=1, le=72),
    db: Session = Depends(get_db),
):
    if not db.get(Bin, bin_id):
        raise HTTPException(404, "bin not found")

    rows = (
        db.execute(
            select(Prediction)
            .where(Prediction.bin_id == bin_id)
            .order_by(Prediction.ts_target)
            .limit(horizon * 12)
        )
        .scalars()
        .all()
    )

    if not rows:
        from app.services.forecaster import forecast_bin

        rows = forecast_bin(db, bin_id, horizon_hours=horizon)
        db.commit()

    return PredictionCurve(
        bin_id=bin_id,
        points=[
            PredictionPoint(
                ts_target=r.ts_target,
                predicted_fill_pct=r.predicted_fill_pct,
                horizon_hours=r.horizon_hours,
            )
            for r in rows
        ],
    )
