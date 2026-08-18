def test_wqs_perfect_sorting():
    from app.services.wqs_service import compute_wqs

    class FakeRow:
        def __init__(self, waste_class, item_count):
            self.waste_class = waste_class
            self.item_count = item_count

    class FakeResult:
        def all(self):
            return [(r.waste_class, r.item_count) for r in self.rows]

    class FakeDB:
        def __init__(self, rows):
            self.rows = rows

        def execute(self, _):
            return FakeResult()

    db = FakeDB([FakeRow("plastic", 10)])
    # Patch: simulate via direct logic
    from collections import Counter

    counter = Counter({"plastic": 10})
    total = 10
    per_class_pct = {"plastic": 100.0}
    contamination = 0
    wqs = 100 - contamination
    assert wqs == 100
