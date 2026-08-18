from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Bin, Classification, DCPIScore, Telemetry, WQSScore
from app.db.schemas import BinCreate, BinDetail, BinOut

router = APIRouter(prefix="/api/v1/bins", tags=["bins"])


@router.get("", response_model=list[BinOut])
def list_bins(db: Session = Depends(get_db)):
    return db.execute(select(Bin).order_by(Bin.id)).scalars().all()


@router.post("", response_model=BinOut, status_code=201)
def create_bin(payload: BinCreate, db: Session = Depends(get_db)):
    bin_ = Bin(**payload.model_dump())
    db.add(bin_)
    db.commit()
    db.refresh(bin_)
    return bin_


@router.get("/{bin_id}", response_model=BinDetail)
def get_bin(bin_id: int, db: Session = Depends(get_db)):
    bin_ = db.get(Bin, bin_id)
    if not bin_:
        raise HTTPException(404, "bin not found")

    tel = db.execute(
        select(Telemetry).where(Telemetry.bin_id == bin_id).order_by(desc(Telemetry.ts)).limit(1)
    ).scalar_one_or_none()

    wqs = db.execute(
        select(WQSScore).where(WQSScore.bin_id == bin_id).order_by(desc(WQSScore.ts)).limit(1)
    ).scalar_one_or_none()

    dcpi = db.execute(
        select(DCPIScore).where(DCPIScore.bin_id == bin_id).order_by(desc(DCPIScore.ts)).limit(1)
    ).scalar_one_or_none()

    cls = db.execute(
        select(Classification)
        .where(Classification.bin_id == bin_id)
        .order_by(desc(Classification.ts))
        .limit(1)
    ).scalar_one_or_none()

    return BinDetail(
        id=bin_.id,
        name=bin_.name,
        district=bin_.district,
        lat=bin_.lat,
        lon=bin_.lon,
        capacity_l=bin_.capacity_l,
        hardware_id=bin_.hardware_id,
        qr_code=bin_.qr_code,
        created_at=bin_.created_at,
        fill_pct=tel.fill_pct if tel else None,
        wqs=wqs.wqs if wqs else None,
        dcpi=dcpi.dcpi if dcpi else None,
        last_classification=cls.waste_class if cls else None,
    )
