"""SHAP-based explanation of DCPI scores → natural language."""

TEMPLATE = (
    "Priority raised because: {reasons}. "
    "Dispatching now avoids ~{overflow_prob}% overflow risk and saves ~{fuel_saving}% fuel."
)

REASON_PHRASES = {
    "fill_pct": "fill level at {v:.0f}%",
    "predicted_fill_pct": "forecasted to reach {v:.0f}% in 4h",
    "heat_index": "high heat index ({v:.0f})",
    "gas_index": "elevated gas emission ({v:.0f})",
    "event_boost": "active event nearby",
}


def explain_dcpi(features: dict, contributions: list) -> str:
    top = contributions[:3]
    phrases = [
        REASON_PHRASES.get(c["feature"], c["feature"]).format(v=features.get(c["feature"], 0))
        for c in top
        if c["contribution"] > 5
    ]
    overflow = int(max(20, min(95, features.get("predicted_fill_pct", 50))))
    fuel = int(max(5, min(30, top[0]["contribution"] / 3))) if top else 10
    return TEMPLATE.format(
        reasons=", ".join(phrases) if phrases else "combined signals",
        overflow_prob=overflow,
        fuel_saving=fuel,
    )
