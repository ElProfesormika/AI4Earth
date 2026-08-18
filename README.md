# SmartWasteAI

A Federated, Explainable AI Framework for Predictive Urban Waste Management with Informal Sector Integration.

**Team:** AI4Earth · **Team Leader:** Housseni YABRE  
**SmartAIthon 2026 · Round 2 submission**

## Demo

40 virtual bins across 4 districts stream telemetry via MQTT → DCPI ranks priority → OR-Tools optimizes routes → React dashboard shows live map, forecasts, KPIs, and Digital Twin.

## Architecture

See [SPEC.md](./SPEC.md) for the full specification.

```
Edge (simulator) → MQTT → FastAPI + TimescaleDB → DCPI / WQS / XGBoost / OR-Tools / SHAP
                                              ↓
                                    React dashboard (6 modules)
```

## Run locally

```bash
git clone <repo> && cd AI4Earth
cp .env.example .env

# Ubuntu 24.04 — Docker Compose (standalone v2, NOT docker-compose-plugin):
sudo apt update && sudo apt install -y docker-compose-v2
# or: make install-compose

make up          # builds & starts all services
# wait ~30s for migrations + seed
open http://localhost:5173
```

API docs: http://localhost:8000/docs

### Smoke test

```bash
chmod +x scripts/smoke_test.sh
make smoke
```

## Contributions

| Code | Description |
|------|-------------|
| **WQS** | Waste Quality Score — sorting quality per bin |
| **DCPI** | Dynamic Collection Priority Index — context-aware urgency |
| **FL** | Federated Learning simulation (`ml/src/federated/`) |
| **XAI** | SHAP-based natural-language dispatch explanations |
| **DT** | Digital Twin what-if scenario simulator |
| **Bridge** | Informal-sector waste-picker app (design + API stub) |

## Project structure

- `backend/` — FastAPI, MQTT ingestion, DCPI, routing, XAI
- `frontend/` — React + Vite dashboard (Live Map, Prediction, Routes, Twin, KPIs, Alerts)
- `simulator/` — 40-bin MQTT telemetry generator
- `ml/` — YOLO fine-tuning, XGBoost forecaster, FL POC
- `mobile/` — Waste-picker app design stubs
- `scripts/` — Seed data, smoke tests

## ML training (optional)

```bash
docker compose run --rm ml python -m src.data.download_datasets
docker compose run --rm ml python -m src.training.train_yolo
```

## License

MIT
