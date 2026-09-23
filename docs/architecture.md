# Architecture

```mermaid
flowchart LR
A[Climate / Environmental Data] --> B[Data Validation & Processing]
B --> C[FastAPI Backend]
C --> D[Impact Assessment]
C --> E[AI Risk Prediction]
C --> F[Anomaly Detection]
C --> G[Recommendation Engine]
D --> H[React Dashboard]
E --> H
F --> H
G --> H
C --> I[(SQLite Demo DB)]
C -. Cloud deployment .-> J[(MongoDB / Cloud DB)]
```

## Technology mapping
- Big Data: large historical dataset, tabular processing and scalable ingestion design.
- AI: Random Forest regression/classification and anomaly detection.
- Cybersecurity: authentication, hashing, JWT, validation, audit logs.
- Cloud Computing: Docker and MongoDB-ready configuration.
