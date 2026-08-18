# SmartWasteAI

A Federated, Explainable AI Framework for Predictive Urban Waste Management with Informal Sector Integration.

**Team:** AI4Earth · **Team Leader:** Housseni YABRE  
**SmartAIthon 2026 · Round 2 submission**

## Demo

40 virtual bins across 4 districts stream telemetry via MQTT → DCPI ranks priority → OR-Tools optimizes routes → React dashboard shows live map, forecasts, KPIs, and Digital Twin.

## Documentation

- [Technical report](./docs/REPORT.md) — problem, architecture, algorithms, API, how to run  
- [Video scripts](./docs/video-scripts.md) — Demo (2–5 min) and Workflow (2 min) voice-over  
- [SPEC.md](./SPEC.md) — full implementation specification  
- [API](./docs/api.md) · [Architecture](./docs/architecture.md) · [Live demo checklist](./docs/demo-script.md)

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
## APP SCREENS


<img width="1917" height="952" alt="Screenshot 2026-08-18 at 09-27-09 SmartWasteAI · Command Center" src="https://github.com/user-attachments/assets/cafb254a-6d01-485a-b768-51446b43ff5f" />

<img width="1917" height="961" alt="Screenshot 2026-08-18 at 09-27-48 SmartWasteAI · Command Center" src="https://github.com/user-attachments/assets/11fa293a-a1d5-44db-9257-479bda5dbefd" />

<img width="1917" height="961" alt="Screenshot 2026-08-18 at 09-28-00 SmartWasteAI · Command Center" src="https://github.com/user-attachments/assets/da9d2f42-8722-40f1-b307-da253365db17" />

<img width="1917" height="961" alt="Screenshot 2026-08-18 at 09-28-15 SmartWasteAI · Command Center" src="https://github.com/user-attachments/assets/50dd19d0-2fba-4df7-98cd-59ba0523e8e4" />

<img width="1917" height="958" alt="Screenshot 2026-08-18 at 09-28-25 SmartWasteAI · Command Center" src="https://github.com/user-attachments/assets/21383fbf-3987-4580-b4a2-ec45363e2904" />

<img width="1917" height="955" alt="Screenshot 2026-08-18 at 09-28-35 SmartWasteAI · Command Center" src="https://github.com/user-attachments/assets/0bc5da5a-c043-4874-ad46-6442a54fac6f" />





## License

MIT
