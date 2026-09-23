# PRJ_666 — Climate Change Impact Assessment and Environmental Risk Prediction Platform

## Official project
- **Project:** PRJ_666
- **Title:** Climate Change Impact Assessment and Environmental Risk Prediction Platform
- **Technology:** Big Data, AI, Cybersecurity, Cloud Computing
- **SDG:** SDG 13 — Climate Action

## What the prototype does
The platform processes environmental observations, calculates a transparent project-specific climate impact score, predicts future energy consumption and environmental risk with ML, detects anomalies, produces alerts/recommendations, and presents results in a secure web dashboard.

### Architecture
React dashboard → FastAPI REST API → analytics/AI/security services → SQLite demo store.
The backend is cloud-ready and includes MongoDB configuration hooks and Docker files. The local SQLite store is intentionally used so the academic demo works without a database server.

## Demo login
**Username:** `admin`  
**Password:** `PRJ666@Demo`

Change the secret/password for any non-demo deployment.

## Run on Windows
1. Install Python 3.11+ and Node.js 20+.
2. Double-click `run_windows.bat`.
3. Open `http://127.0.0.1:5173`.

Or manually:
```powershell
cd backend
py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m ml.train_model
uvicorn app.main:app --reload --port 8000
```
In another terminal:
```powershell
cd frontend
npm install
npm run dev
```

## Run on macOS/Linux
```bash
chmod +x run_mac_linux.sh
./run_mac_linux.sh
```

## ML
Two models are trained:
1. Random Forest Regressor — predicts `energy_kwh`.
2. Random Forest Classifier — predicts `risk_level`.

The training script reports MAE, RMSE, R² and classification accuracy. Metrics shown by the app are calculated from the included **synthetic demonstration dataset**; they are not claims about real-world performance.

## Big Data component
The sample dataset is 2,200 daily observations. For a larger deployment, the preprocessing approach can be extended to chunked Pandas ingestion, object storage and distributed processing. The academic prototype intentionally stays laptop-friendly.

## Cybersecurity
- bcrypt password hashing
- JWT access tokens
- authenticated API routes
- role check for destructive admin operation
- Pydantic input validation
- CORS restriction
- audit logging
- environment-variable configuration for secrets

## Cloud readiness
Dockerfiles and `docker-compose.yml` are included. `MONGODB_URI` can be configured for a cloud MongoDB deployment. The local default remains self-contained for reliable demonstration.

## Data note
`backend/data/climate_data.csv` is synthetic demonstration data created for this academic prototype. Replace it with authoritative observations for real research or operational use.

## API
- `POST /api/auth/login`
- `GET /api/dashboard`
- `GET /api/analytics`
- `GET /api/environmental-data`
- `POST /api/environmental-data`
- `DELETE /api/environmental-data/{id}`
- `POST /api/predict`
- `GET /api/model-metrics`
- `GET /api/anomalies`
- `GET /api/alerts`
- `GET /api/recommendations`
- `GET /api/integrations`

FastAPI docs: `http://127.0.0.1:8000/docs`

## SDG 13
The platform supports SDG 13 by enabling climate/environmental monitoring, risk assessment, prediction, anomaly alerts and data-driven decision support.

## Limitations
- Demonstration dataset is synthetic.
- The impact score is a project-specific indicator, not an official climate-risk standard.
- Emission factor is configurable and should be replaced with an authoritative regional factor for real use.
- Predictions depend on the quality and representativeness of training data.
- Cloud deployment requires production security hardening.

## Future scope
- Real-time IoT ingestion
- Satellite/weather datasets
- Distributed Big Data processing
- Geospatial risk maps
- Explainable AI
- Cloud object storage
- Managed MongoDB
- Role-based organizational tenancy
- Real-time notification services
