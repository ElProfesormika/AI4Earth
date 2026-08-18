# API Reference

Base URL: `http://localhost:8000/api/v1`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/bins` | List bins |
| GET | `/bins/{id}` | Bin detail |
| GET | `/telemetry/latest` | Latest telemetry per bin |
| GET | `/dcpi` | DCPI ranking |
| GET | `/dcpi/{bin_id}` | DCPI detail |
| GET | `/predictions/{bin_id}` | Fill forecast |
| GET | `/routes/today` | Today's route |
| POST | `/routes/optimize` | Trigger OR-Tools optimization |
| GET | `/xai/{dcpi_id}` | SHAP explanation |
| POST | `/digital-twin/simulate` | What-if scenario |
| GET | `/kpis/summary` | Aggregate KPIs |
| GET | `/workers` | List waste pickers |
| POST | `/workers/{id}/scan` | QR collection event |

Interactive docs: http://localhost:8000/docs
