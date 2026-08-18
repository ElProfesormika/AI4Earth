from fastapi import APIRouter

from app.db.schemas import HealthOut

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthOut)
def health():
    return HealthOut(status="ok")
