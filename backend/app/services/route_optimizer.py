"""Vehicle-routing on top DCPI bins. Simplified TSP with capacity constraint."""
from datetime import datetime
from math import asin, cos, radians, sin, sqrt

from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from sqlalchemy import desc, func, select

from app.db.models import Bin, DCPIScore, Route
from app.db.session import SessionLocal

DEPOT_LAT, DEPOT_LON = 12.9716, 77.5946
MAX_BINS_PER_ROUTE = 15
MIN_DCPI_TO_COLLECT = 40.0


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    r = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [a[0], a[1], b[0], b[1]])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    return 2 * r * asin(sqrt(sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2))


def optimize_today() -> dict:
    with SessionLocal() as db:
        subq = (
            select(DCPIScore.bin_id, func.max(DCPIScore.ts).label("max_ts"))
            .group_by(DCPIScore.bin_id)
            .subquery()
        )
        rows = db.execute(
            select(Bin.id, Bin.lat, Bin.lon, DCPIScore.dcpi)
            .join(DCPIScore, DCPIScore.bin_id == Bin.id)
            .join(
                subq,
                (DCPIScore.bin_id == subq.c.bin_id) & (DCPIScore.ts == subq.c.max_ts),
            )
            .where(DCPIScore.dcpi >= MIN_DCPI_TO_COLLECT)
            .order_by(desc(DCPIScore.dcpi))
            .limit(MAX_BINS_PER_ROUTE)
        ).all()

        if not rows:
            return {"stops": [], "distance_km": 0.0}

        pts = [(DEPOT_LAT, DEPOT_LON)] + [(r.lat, r.lon) for r in rows]
        n = len(pts)
        dist = [[int(haversine_km(pts[i], pts[j]) * 1000) for j in range(n)] for i in range(n)]

        manager = pywrapcp.RoutingIndexManager(n, 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def dist_cb(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return dist[from_node][to_node]

        transit_idx = routing.RegisterTransitCallback(dist_cb)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        sol = routing.SolveWithParameters(params)

        stops, total_m = [], 0
        idx = routing.Start(0)
        while not routing.IsEnd(idx):
            node = manager.IndexToNode(idx)
            if node > 0:
                stops.append(rows[node - 1].id)
            next_idx = sol.Value(routing.NextVar(idx))
            total_m += routing.GetArcCostForVehicle(idx, next_idx, 0)
            idx = next_idx

        distance_km = total_m / 1000
        baseline_km = sum(haversine_km(pts[0], p) * 2 for p in pts[1:])
        saving_pct = (
            round(max(0.0, (1 - distance_km / baseline_km) * 100), 1) if baseline_km else 0.0
        )

        route = Route(
            ts=datetime.utcnow(),
            truck_id="truck-1",
            stops=stops,
            distance_km=distance_km,
            expected_fuel_saving_pct=saving_pct,
            expected_co2_saving_kg=round(distance_km * 0.35, 2),
        )
        db.add(route)
        db.commit()
        db.refresh(route)
        return {
            "id": route.id,
            "stops": stops,
            "distance_km": distance_km,
            "expected_fuel_saving_pct": saving_pct,
            "expected_co2_saving_kg": route.expected_co2_saving_kg,
        }
