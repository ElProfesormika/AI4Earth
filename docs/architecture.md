# Architecture

Three tiers + informal sector bridge (see SPEC.md section 2).

1. **Tier 1 — Edge:** Camera + sensors (simulated by `simulator/`)
2. **Tier 2 — Federated Cloud:** MQTT → PostgreSQL/TimescaleDB, XGBoost forecaster
3. **Tier 3 — Decision:** DCPI, OR-Tools routing, SHAP XAI, Digital Twin
4. **Bridge:** Worker QR scan API (`/api/v1/workers/{id}/scan`)

Data flow: simulator publishes every 5 s → backend ingests → DCPI recomputed every 30 s → frontend polls every 5 s.
