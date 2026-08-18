from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Bin, Classification
from app.db.schemas import ClassificationCreate, ClassificationOut
from app.services.wqs_service import compute_and_store_wqs

router = APIRouter(prefix="/api/v1/classifications", tags=["classifications"])


@router.get("/{bin_id}", response_model=list[ClassificationOut])
def list_classifications(
    bin_id: int,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    if not db.get(Bin, bin_id):
        raise HTTPException(404, "bin not found")
    return (
        db.execute(
            select(Classification)
            .where(Classification.bin_id == bin_id)
            .order_by(desc(Classification.ts))
            .limit(limit)
        )
        .scalars()
        .all()
    )


@router.post("", response_model=ClassificationOut, status_code=201)
def create_classification(payload: ClassificationCreate, db: Session = Depends(get_db)):
    if not db.get(Bin, payload.bin_id):
        raise HTTPException(404, "bin not found")
    row = Classification(
        bin_id=payload.bin_id,
        ts=datetime.utcnow(),
        waste_class=payload.waste_class,
        confidence=payload.confidence,
        item_count=payload.item_count,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    compute_and_store_wqs(db, payload.bin_id)
    db.commit()
    return row
