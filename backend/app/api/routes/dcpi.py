from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Bin, DCPIScore
from app.db.schemas import DCPIDetail, DCPIItem

router = APIRouter(prefix="/api/v1/dcpi", tags=["dcpi"])


@router.get("", response_model=list[DCPIItem])
def list_dcpi(db: Session = Depends(get_db)):
    subq = (
        select(
            DCPIScore.bin_id,
            func.max(DCPIScore.ts).label("max_ts"),
        )
        .group_by(DCPIScore.bin_id)
        .subquery()
    )
    rows = db.execute(
        select(Bin, DCPIScore)
        .join(DCPIScore, DCPIScore.bin_id == Bin.id)
        .join(subq, (DCPIScore.bin_id == subq.c.bin_id) & (DCPIScore.ts == subq.c.max_ts))
        .order_by(desc(DCPIScore.dcpi))
    ).all()

    return [
        DCPIItem(
            bin_id=b.id,
            name=b.name,
            district=b.district,
            lat=b.lat,
            lon=b.lon,
            dcpi=s.dcpi,
            ts=s.ts,
        )
        for b, s in rows
    ]


@router.get("/{bin_id}", response_model=DCPIDetail)
def get_dcpi(bin_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        select(DCPIScore).where(DCPIScore.bin_id == bin_id).order_by(desc(DCPIScore.ts)).limit(1)
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(404, "no DCPI yet for this bin")
    return DCPIDetail(
        bin_id=bin_id,
        dcpi=row.dcpi,
        ts=row.ts,
        features=row.features,
        reasons=row.reasons,
    )
