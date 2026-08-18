from fastapi import APIRouter

from app.db.schemas import SimulationRequest, SimulationResult
from app.services.digital_twin import run_simulation

router = APIRouter(prefix="/api/v1/digital-twin", tags=["digital-twin"])


@router.post("/simulate", response_model=SimulationResult)
def simulate(payload: SimulationRequest):
    return run_simulation(payload)
