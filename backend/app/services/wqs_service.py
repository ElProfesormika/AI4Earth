from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy import select

from app.db.models import Classification, WQSScore

WASTE_CLASSES = ["plastic", "paper", "glass", "metal", "organic", "ewaste"]


def compute_wqs(db, bin_id: int, window_minutes: int = 60) -> dict:
    since = datetime.utcnow() - timedelta(minutes=window_minutes)
    rows = db.execute(
        select(Classification.waste_class, Classification.item_count).where(
            Classification.bin_id == bin_id,
            Classification.ts >= since,
        )
    ).all()
    if not rows:
        return {"wqs": 0.0, "contamination_pct": 0.0, "per_class_pct": {}}

    counter = Counter()
    for cls, n in rows:
        counter[cls] += n
    total = sum(counter.values())
    per_class_pct = {k: round(100 * v / total, 1) for k, v in counter.items()}
    dominant = counter.most_common(1)[0][0]
    contamination = 100 - per_class_pct[dominant]
    return {
        "wqs": round(100 - contamination, 1),
        "contamination_pct": round(contamination, 1),
        "per_class_pct": per_class_pct,
        "dominant_class": dominant,
    }


def compute_and_store_wqs(db, bin_id: int) -> WQSScore | None:
    result = compute_wqs(db, bin_id)
    if not result.get("per_class_pct"):
        return None
    row = WQSScore(
        bin_id=bin_id,
        ts=datetime.utcnow(),
        wqs=result["wqs"],
        contamination_pct=result["contamination_pct"],
        per_class_pct=result["per_class_pct"],
    )
    db.add(row)
    return row


def recompute_all_wqs():
    from app.db.models import Bin
    from app.db.session import SessionLocal

    with SessionLocal() as db:
        for bin_ in db.execute(select(Bin)).scalars():
            compute_and_store_wqs(db, bin_.id)
        db.commit()
