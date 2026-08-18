# 5-minute live demo

1. `make up` — boot all services (~30 s)
2. Open http://localhost:5173
3. **Live Map** — 40 bins color-coded by DCPI, auto-refresh every 5 s
4. Click a red/orange bin → **Bin Detail** panel shows DCPI score + top reasons
5. **Prediction** tab → 24 h fill forecast curve for selected bin
6. **Routes** → click **Optimize Route** → truck tour on map + fuel/CO₂ KPIs
7. **Digital Twin** → 3D city view → run "festival scenario"
8. **KPIs** → aggregate WQS, CO₂, workers, payments
9. **Alerts** → critical/high priority bins with explanations
10. Close with **mobile app screens** in `mobile/` (design stub)

## Smoke test

```bash
make smoke
```
