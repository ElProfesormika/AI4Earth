from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Bin, Collection, Worker
from app.db.schemas import CollectionOut, ScanRequest, WorkerOut

router = APIRouter(prefix="/api/v1/workers", tags=["workers"])

PAYMENT_RATE = Decimal("0.50")  # per kg


@router.get("", response_model=list[WorkerOut])
def list_workers(db: Session = Depends(get_db)):
    return db.execute(select(Worker).order_by(Worker.id)).scalars().all()


@router.post("/{worker_id}/scan", response_model=CollectionOut, status_code=201)
def worker_scan(worker_id: int, payload: ScanRequest, db: Session = Depends(get_db)):
    worker = db.get(Worker, worker_id)
    if not worker or not worker.active:
        raise HTTPException(404, "worker not found or inactive")

    bin_ = db.execute(select(Bin).where(Bin.qr_code == payload.qr_code)).scalar_one_or_none()
    if not bin_:
        raise HTTPException(404, "bin QR not recognized")

    payment = Decimal(str(round(float(payload.weight_kg) * float(PAYMENT_RATE), 2)))
    collection = Collection(
        worker_id=worker_id,
        bin_id=bin_.id,
        ts=datetime.utcnow(),
        qr_scan=payload.qr_code,
        weight_kg=payload.weight_kg,
        payment_amount=payment,
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection
