from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import DCPIScore, XAIExplanation
from app.db.schemas import XAIExplanationOut
from app.services.xai_engine import get_or_create_explanation

router = APIRouter(prefix="/api/v1/xai", tags=["xai"])


@router.get("/{dcpi_id}", response_model=XAIExplanationOut)
def get_xai(dcpi_id: int, db: Session = Depends(get_db)):
    dcpi = db.get(DCPIScore, dcpi_id)
    if not dcpi:
        raise HTTPException(404, "DCPI score not found")
    explanation = get_or_create_explanation(db, dcpi)
    db.commit()
    return explanation
