# SmartWasteAI — Technical Project Write-Up

**Team:** AI4Earth  
**Team leader:** Housseni YABRE  
**Teammates:** Kossi Sylvanus AMEYIDA · Rich DEGBEVI  
**Competition:** SmartAIthon 2026 · Round 2  
**Theme:** Smart Waste Management Systems  

This page is intended to serve as the **technical documentation / blog-style project write-up** for SmartWasteAI. It goes deeper than the presentation deck by explaining the actual implementation choices, data flow, algorithms, API design, UI behavior, deployment setup, and current limitations.

---

## Why we built SmartWasteAI

Municipal waste collection is still largely reactive. Most existing “smart bin” products stop at one signal: **fill level**. That helps, but it does not solve the deeper operational problem.

A bin that is 90% full is not always the most urgent one. A bin at 70% in a crowded market, under high temperature, with elevated gas emissions and an active city event nearby may be operationally more dangerous. In addition, municipalities rarely get visibility into **sorting quality**, and almost never integrate the **informal sector** that already handles a significant share of recyclable recovery.

SmartWasteAI was designed to address that gap. Instead of asking only *“which bin is full?”*, the system asks:

- Which bin is most urgent **right now**?
- Which one will become urgent **soon**?
- Why was a dispatch decision made?
- How does sorting quality affect downstream recovery?
- How can informal waste pickers be connected to the digital workflow?

The result is not a citizen-facing app. It is a **municipal operator command center** backed by a streaming backend and decision-support services.

---

## What the prototype demonstrates

The current prototype delivers a complete software loop:

1. A **sensor simulator** publishes telemetry for 40 virtual bins across 4 districts.
2. A backend MQTT listener ingests this data into **PostgreSQL + TimescaleDB**.
3. The system computes:
   - **WQS** — Waste Quality Score
   - **DCPI** — Dynamic Collection Priority Index
   - **fill forecasts** for the next 24 hours
4. The routing layer uses **Google OR-Tools** to optimize a collection tour.
5. The explainability layer exposes **feature contributions** and natural-language reasoning.
6. A React dashboard visualizes the city state through:
   - Live Map
   - Prediction
   - Routes
   - Digital Twin
   - KPIs
   - Alerts
7. A worker collection API provides the first building block for **informal-sector integration**.

This is the important distinction for judges: the system is not only a concept. It already behaves like an end-to-end operational platform, even though some ML parts are still in “scaffold / fallback / simulation” mode for the competition deadline.

---

## System architecture

SmartWasteAI follows a three-tier architecture with a social bridge.

### Tier 1 — Edge

In the target architecture, each smart bin would include:

- a camera
- an ultrasonic fill sensor
- a load cell
- temperature and humidity sensing
- a gas sensor
- a Raspberry Pi 4 running local inference

For the MVP, we replaced physical hardware with a **simulator**. This allowed us to validate the full software stack without waiting for devices, procurement, or field wiring.

### Tier 2 — Federated Cloud

This layer receives and stores the stream:

- **Mosquitto** handles MQTT messaging
- **FastAPI** hosts the backend API and ingestion logic
- **TimescaleDB** stores time-series telemetry efficiently
- background jobs compute WQS, forecasts, and DCPI on a schedule

### Tier 3 — Decision Layer

This is the intelligence layer:

- DCPI scoring
- forecasting
- route optimization
- explainability
- digital twin scenario simulation

### Informal-sector bridge

A dedicated API exists for QR-based collection tracking:

- worker scans a bin QR code
- collected weight is logged
- a micropayment amount is recorded

The mobile app itself remains a design stub in this sprint, but the backend contract already exists.

---

## Data flow end to end

The system loop is straightforward and intentionally modular:

1. The simulator generates telemetry for a virtual city.
2. Each bin publishes to:

```text
smartwaste/bins/{bin_id}/telemetry
```

3. The backend MQTT listener subscribes to telemetry and bin registration topics.
4. Telemetry rows are persisted into the `telemetry` hypertable.
5. Periodic jobs recompute:
   - WQS every 2 minutes
   - DCPI every 30 seconds
   - forecasts every 5 minutes
6. The frontend polls the REST API every 5 seconds.
7. Operators interact with the dashboard:
   - click bins
   - inspect reasons
   - trigger route optimization
   - run a digital twin scenario

This architecture is one of the strengths of the project: the UI is cleanly separated from the streaming and scoring logic, so the system remains understandable under demo pressure.

---

## Backend implementation details

The backend is built with **FastAPI** and structured around a small set of responsibilities:

- data ingestion
- storage
- scheduled recomputation
- REST delivery

### Database design

The database contains both relational and time-series entities:

- `bins`
- `telemetry`
- `classifications`
- `wqs_scores`
- `dcpi_scores`
- `predictions`
- `routes`
- `xai_explanations`
- `workers`
- `collections`
- `city_events`

The most important table for scalability is `telemetry`, which is converted into a **TimescaleDB hypertable**. This matters because sensor systems create large append-only streams, and ordinary relational tables become less convenient as volume grows.

### Scheduler behavior

The backend starts an async scheduler on application startup:

- `recompute_all_dcpi()` every 30 seconds
- `recompute_forecasts()` every 5 minutes
- `recompute_all_wqs()` every 2 minutes

This gives the prototype a “live city” behavior without requiring manual refresh or admin actions.

### REST API surface

The API is organized around operational tasks, not just CRUD:

- health and telemetry access
- bin inspection
- prediction retrieval
- DCPI ranking
- route optimization
- XAI explanations
- digital twin simulation
- worker collection events
- KPI summary

This is important from a hackathon scoring perspective: the API is not merely a storage interface. It exposes **decision products**.

---

## Waste Quality Score (WQS)

WQS is one of the novel contributions in the project. It reflects how “clean” or consistent the material stream is inside a bin.

### Why WQS matters

A full bin does not tell us whether its contents are useful to recyclers. A city that improves recovery rates needs not only efficient collection but also visibility into **stream quality**.

### Current implementation

In the MVP, WQS is computed from waste classifications over a rolling window:

1. count the classified waste items in the recent window
2. determine the dominant class
3. treat everything else as contamination

Formula:

```text
WQS = 100 − contamination_pct
```

### Interpretation

- high WQS: mostly mono-material stream
- low WQS: mixed or contaminated stream

### Current limitation

In a hardware deployment, classifications would come from a real on-device vision model. In the prototype, classifications are generated from the simulated flow so that downstream modules can be exercised end to end.

---

## Forecasting design

The forecasting layer is designed around **XGBoost**.

### Target model

The intended features are:

- hour of day
- day of week
- current fill
- recent fill deltas
- temperature
- humidity
- gas
- event flag

The objective is to predict future fill at a defined horizon.

### Why XGBoost

We selected XGBoost because:

- it performs well on tabular time-aware operational data
- it is lightweight compared to sequence-heavy deep models
- it is easier to debug in a hackathon setting
- it works well with explainability tooling

### Fallback behavior

If no trained `xgb_forecaster.json` is available, the backend uses a **rule-based incremental forecast**. This was a practical decision: a missing model should not break the dashboard or demo flow.

This is a good example of engineering trade-off under time pressure. A hackathon demo should degrade gracefully rather than collapse because a model artifact is missing.

---

## DCPI — Dynamic Collection Priority Index

DCPI is the core decision score of SmartWasteAI.

### Motivation

Static thresholding is too simplistic. A fill threshold alone misses contextual urgency.

### Formula

The current score combines five terms:

| Feature | Weight | Meaning |
|---|---|---|
| Current fill % | 0.35 | present fullness |
| Predicted fill % | 0.25 | near-future overflow risk |
| Heat index | 0.10 | thermal risk |
| Gas index | 0.15 | methane / odor proxy |
| Event boost | 0.15 | demand shock from local events |

### Example reasoning

A bin in the **Market** district can receive a much higher priority during a festival because:

- fill rises faster
- forecast rises faster
- surrounding activity makes overflow more likely

This is precisely the kind of operational nuance a simple “80% full” trigger cannot capture.

### Explainability

The backend stores:

- the input feature vector
- the top feature contributions

The frontend then turns these into operator-readable bars and labels. This is not full SHAP on a production model yet, but the pipeline is already explainability-oriented by design.

---

## Route optimization

The routing layer uses **Google OR-Tools**.

### Current approach

The optimizer:

1. selects bins above the DCPI threshold
2. caps the problem size for the MVP
3. computes geographic distances using haversine
4. solves an ordered tour from a depot

### Why OR-Tools

OR-Tools is a strong fit for this use case because:

- it is production-grade
- it is widely understood
- it solves constrained routing reliably
- it is easier to justify than an ad hoc heuristic

### Output metrics

For demo clarity, the route service reports:

- ordered stops
- route distance
- expected fuel saving
- estimated CO2 saving

This makes the optimization tangible for judges. It is not just a line on a map; it is a measurable decision artifact.

---

## Explainability layer

The project uses a practical XAI design:

- keep the scoring formula interpretable
- store feature-level contributions
- turn them into natural-language explanations

### Why this matters

Many urban AI dashboards fail because they tell operators *what* to do but not *why*. In a municipal context, trust is operational. Dispatch choices need to be explainable to managers, supervisors, and field teams.

### Frontend presentation

The inspector panel shows:

- total DCPI
- qualitative urgency state
- ranked reasons
- sensor snapshot

This is intentionally always visible on the right side of the dashboard. It behaves like an “explain this decision” surface rather than a hidden debug panel.

---

## Digital Twin

The Digital Twin is implemented as a lightweight but meaningful simulation layer.

### What it does in the MVP

- renders bins in a 3D scene
- maps height to priority
- maps color to urgency
- allows a “festival” scenario to be triggered
- returns before / after DCPI behavior

### Why it matters

This gives operators a scenario-testing surface:

- what happens if waste generation spikes in a district?
- which bins become critical first?
- how would collection planning shift?

The twin is intentionally simple in geometry but useful in decision logic.

---

## Simulator design

The simulator is more than random number generation. It approximates a city with structured behavior.

### City layout

The MVP defines four districts:

- Downtown
- Residential-North
- Market
- Industrial

Each district has:

- a fixed number of bins
- a center coordinate
- a characteristic fill-rate range

### Environmental dynamics

The simulator includes:

- daily temperature oscillation
- humidity coupling
- gas growth with fill and heat
- city events with multipliers
- reset behavior that imitates collection

### Why simulation was the right choice

For a 72-hour sprint, simulation made it possible to:

- test ingest volume
- validate the API
- demonstrate prediction and ranking
- feed the UI continuously

without depending on physical hardware.

---

## Frontend design and user flow

The frontend is a **dark command-center interface** built with React, Vite, Tailwind, Leaflet, Recharts, and Three.js.

### Pages

**Live Map**  
Shows all bins as urgency-coded markers. Clicking a marker populates the XAI inspector.

**Prediction**  
Displays the selected bin’s forecast curve over the next 24 hours.

**Routes**  
Lets the operator trigger optimization and view route geometry plus operational KPIs.

**Digital Twin**  
Offers a 3D scenario exploration mode.

**KPIs**  
Summarizes system-level impact metrics.

**Alerts**  
Surfaces critical and high-priority bins as an action queue.

### Interaction model

The frontend does not connect directly to MQTT. It only consumes the REST API. This is a good engineering boundary:

- streaming complexity stays in the backend
- the UI remains replaceable
- debugging is easier

---

## ML roadmap beyond the demo

The hackathon build is intentionally honest about what is complete and what is scaffolded.

### YOLO vision pipeline

The ML folder specifies:

- **YOLOv8n**
- target classes:
  - plastic
  - paper
  - glass
  - metal
  - organic
  - e-waste
- dataset strategy:
  - TrashNet
  - TACO

### Why YOLOv8n

YOLOv8n was selected because it is:

- small enough for edge deployment
- easy to fine-tune quickly
- exportable toward TFLite INT8
- well documented and practical for hackathon work

### Current status

For this round:

- the dataset and training structure are prepared
- the training script exists
- the operational backend is already ready to consume outputs

What is not claimed:

- final mAP benchmarks
- live camera inference FPS on a physical Pi
- real-world confusion matrices from this sprint

This distinction is important. We do not want the blog to overclaim what the PPT cannot defend.

---

## Informal-sector bridge

This is one of the strongest differentiators of the project.

Most smart-waste systems optimize truck logistics while ignoring the actors already recovering materials on the ground. SmartWasteAI includes an explicit bridge:

- workers exist as first-class backend entities
- a QR flow logs collection events
- payment amounts are recorded
- mobile screens are already documented

### Why this matters technically

This is not only social framing. It changes the data model and workflow:

- bins need QR identity
- collections need timestamped attribution
- district-level coordination can include informal actors

This creates a future path toward traceability from bin to picker to recycler.

---

## Deployment and local run

SmartWasteAI is packaged with Docker Compose for reproducibility.

### Services

- `db`
- `mqtt`
- `backend`
- `simulator`
- `frontend`

### Run steps

```bash
cp .env.example .env
make up
make smoke
```

The smoke test checks:

1. API health
2. bin registration
3. telemetry availability
4. DCPI computation
5. route optimization
6. KPI summary

This matters for judging because it proves the platform can be run as a cohesive system, not only as disconnected screenshots.

---

## What shipped and what did not

### Shipped

- live simulator
- MQTT ingestion
- Timescale-backed telemetry storage
- WQS
- DCPI
- forecast endpoint
- route optimization
- XAI inspector
- digital twin
- worker collection API
- polished dashboard

### Partially shipped / scaffolded

- YOLO training pipeline
- Flower federated learning simulation
- mobile companion app

### Not shipped in this round

- physical Raspberry Pi deployment
- real sensor electronics
- production payment system
- live federated rounds with hardware clients

This cut-line was deliberate. We prioritized a **working end-to-end prototype** over unfinished hardware theater.

---

## Why this project is technically meaningful

The value of SmartWasteAI is not in any single library. It is in how the components are composed:

- streaming ingestion
- time-series storage
- explainable scoring
- predictive planning
- optimization
- a usable operator interface

The project also shows strong architectural judgment for a hackathon:

- simulation replaced unavailable hardware without breaking the architecture
- graceful fallbacks were added where model artifacts may be absent
- explainability is embedded in the product, not bolted on later
- the social bridge is represented in the API and schema, not only in slides

---

## Future work

The most important next steps are clear:

1. train and benchmark the YOLOv8n waste classifier
2. deploy the edge stack on a real Raspberry Pi
3. replace simulated classifications with live camera inference
4. run a true Flower multi-client experiment
5. implement the picker mobile app
6. connect with a municipal or NGO pilot partner

At that point, SmartWasteAI could move from a strong hackathon system into a publishable and field-testable platform.

---

## Submission references

| Asset | Location |
|---|---|
| Full specification | `SPEC.md` |
| This technical write-up | `docs/REPORT.md` |
| Video scripts | `docs/video-scripts.md` |
| API reference | `docs/api.md` |
| Demo checklist | `docs/demo-script.md` |

---

SmartWasteAI is our attempt to move waste management from passive monitoring to **predictive, explainable, and socially inclusive urban intelligence**.
