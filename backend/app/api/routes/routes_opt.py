from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Route
from app.db.schemas import RouteOut
from app.services.route_optimizer import optimize_today

router = APIRouter(prefix="/api/v1/routes", tags=["routes"])


@router.get("/today", response_model=RouteOut | None)
def route_today(db: Session = Depends(get_db)):
    row = db.execute(select(Route).order_by(desc(Route.ts)).limit(1)).scalar_one_or_none()
    return row


@router.post("/optimize", response_model=RouteOut)
def optimize_route(db: Session = Depends(get_db)):
    result = optimize_today()
    if not result.get("stops"):
        raise HTTPException(404, "no bins above DCPI threshold for routing")
    row = db.get(Route, result["id"])
    if not row:
        raise HTTPException(500, "route optimization failed")
    return row
