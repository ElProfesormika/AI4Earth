"""Seed demo data: workers, city events, optional bins if simulator hasn't registered yet."""
import random
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from sqlalchemy import select

from app.db.models import Bin, CityEvent, Worker
from app.db.session import SessionLocal
from app.services.dcpi_service import recompute_all_dcpi

CONFIG_PATH = Path("/app/simulator/config/city_config.yaml")
if not CONFIG_PATH.exists():
    CONFIG_PATH = Path(__file__).resolve().parents[1] / "simulator" / "config" / "city_config.yaml"


def seed_bins_from_config(db):
    if db.execute(select(Bin)).first():
        return
    if not CONFIG_PATH.exists():
        return
    config = yaml.safe_load(CONFIG_PATH.read_text())
    bin_id = 1
    for d in config["districts"]:
        lat_c, lon_c = d["center"]
        for i in range(d["bins"]):
            db.add(
                Bin(
                    id=bin_id,
                    name=f"{d['name']}-{i + 1}",
                    district=d["name"],
                    lat=lat_c + random.uniform(-0.008, 0.008),
                    lon=lon_c + random.uniform(-0.008, 0.008),
                    capacity_l=120,
                    qr_code=f"QR-{bin_id:04d}",
                )
            )
            bin_id += 1
    db.commit()


def seed_workers(db):
    if db.execute(select(Worker)).first():
        return
    workers = [
        ("Amara K.", "+22890123456", "Market"),
        ("Jean-Paul M.", "+22890234567", "Downtown"),
        ("Fatou S.", "+22890345678", "Residential-North"),
        ("Kofi A.", "+22890456789", "Industrial"),
    ]
    for name, phone, district in workers:
        db.add(Worker(name=name, phone=phone, district=district, active=True))
    db.commit()


def seed_events(db):
    if db.execute(select(CityEvent)).first():
        return
    now = datetime.utcnow()
    db.add(
        CityEvent(
            name="Weekend Market Festival",
            district="Market",
            start_ts=now + timedelta(hours=6),
            end_ts=now + timedelta(hours=18),
            expected_multiplier=2.5,
        )
    )
    db.commit()


def main():
    with SessionLocal() as db:
        seed_bins_from_config(db)
        seed_workers(db)
        seed_events(db)
    recompute_all_dcpi()
    print("Demo data seeded.")


if __name__ == "__main__":
    main()
