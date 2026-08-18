from sqlalchemy import desc, func, select

from app.db.models import Bin, DCPIScore
from app.db.schemas import SimulationRequest, SimulationResult
from app.db.session import SessionLocal
from app.services.dcpi_service import compute_dcpi_for_bin


def run_simulation(payload: SimulationRequest) -> SimulationResult:
    with SessionLocal() as db:
        query = select(Bin)
        if payload.district:
            query = query.where(Bin.district == payload.district)
        bins = db.execute(query).scalars().all()

        if not bins:
            return SimulationResult(
                scenario=payload.scenario,
                district=payload.district,
                bins_affected=0,
                avg_dcpi_before=0.0,
                avg_dcpi_after=0.0,
                message="No bins found for scenario",
            )

        subq = (
            select(DCPIScore.bin_id, func.max(DCPIScore.ts).label("max_ts"))
            .group_by(DCPIScore.bin_id)
            .subquery()
        )
        latest = {
            row.bin_id: row.dcpi
            for row in db.execute(
                select(DCPIScore).join(
                    subq,
                    (DCPIScore.bin_id == subq.c.bin_id) & (DCPIScore.ts == subq.c.max_ts),
                )
            ).scalars()
        }

        before_vals = [latest.get(b.id, 0.0) for b in bins]
        after_vals = []
        for b in bins:
            score, feats, _ = compute_dcpi_for_bin(b.id, db)
            if payload.scenario == "festival" and (
                payload.district is None or b.district == payload.district
            ):
                boosted = min(
                    100.0,
                    score + feats.get("fill_pct", 0) * (payload.event_multiplier - 1) * 0.1,
                )
                after_vals.append(boosted)
            else:
                after_vals.append(score)

        avg_before = round(sum(before_vals) / len(before_vals), 1)
        avg_after = round(sum(after_vals) / len(after_vals), 1)
        msg = (
            f"Scenario '{payload.scenario}': DCPI shifts from {avg_before} to {avg_after} "
            f"across {len(bins)} bins."
        )
        return SimulationResult(
            scenario=payload.scenario,
            district=payload.district,
            bins_affected=len(bins),
            avg_dcpi_before=avg_before,
            avg_dcpi_after=avg_after,
            message=msg,
        )
