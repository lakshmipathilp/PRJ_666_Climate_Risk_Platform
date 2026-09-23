from pathlib import Path
import json, statistics
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .database import init_db, seed_data, get_db
from .schemas import LoginRequest, EnvironmentalCreate, PredictionInput
from .security import hash_password, verify_password, create_access_token, get_current_user
from .services import calculate_impact, risk_from_score, recommendations, detect_anomalies
from .ml import predict, ensure_models
from .config import EMISSION_FACTOR_KG_PER_KWH, MODEL_DIR, DATA_DIR

app = FastAPI(title="PRJ_666 Climate Risk Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

@app.on_event("startup")
def startup():
    init_db()
    seed_data()
    with get_db() as db:
        if not db.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
            db.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                       ("admin", hash_password("PRJ666@Demo"), "admin"))
    ensure_models()

def audit(user, action, detail=""):
    with get_db() as db:
        db.execute("INSERT INTO audit_logs(username,action,detail) VALUES(?,?,?)",
                   (user.get("username"), action, detail))

@app.get("/api/health")
def health():
    return {"status":"ok","project":"PRJ_666","provider":"local-demo"}

@app.post("/api/auth/login")
def login(payload: LoginRequest):
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE username=?", (payload.username,)).fetchone()
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(user["username"], user["role"])
    audit({"username": user["username"]}, "LOGIN")
    return {"access_token": token, "token_type": "bearer", "username": user["username"], "role": user["role"]}

@app.get("/api/me")
def me(user=Depends(get_current_user)):
    return user

@app.get("/api/dashboard")
def dashboard(user=Depends(get_current_user)):
    with get_db() as db:
        rows = db.execute("SELECT * FROM environmental_data ORDER BY date DESC LIMIT 365").fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty: raise HTTPException(404, "No data")
    latest = df.iloc[0].to_dict()
    impact = calculate_impact(latest)
    emission = latest["energy_kwh"] * EMISSION_FACTOR_KG_PER_KWH
    anomalies = detect_anomalies(df).iloc[0]["anomaly"]
    return {
        "latest": latest,
        "impact_score": impact,
        "risk_level": risk_from_score(impact),
        "estimated_co2_kg": round(float(emission),2),
        "anomaly": bool(anomalies),
        "recommendations": [{"severity":s,"message":m} for s,m in recommendations(latest)],
        "emission_factor": EMISSION_FACTOR_KG_PER_KWH
    }

@app.get("/api/analytics")
def analytics(user=Depends(get_current_user)):
    with get_db() as db:
        rows = db.execute("SELECT * FROM environmental_data ORDER BY date ASC").fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    df["estimated_co2_kg"] = df["energy_kwh"] * EMISSION_FACTOR_KG_PER_KWH
    df["impact_score"] = df.apply(calculate_impact, axis=1)
    monthly = df.assign(month=df["date"].str[:7]).groupby("month", as_index=False).agg(
        energy_kwh=("energy_kwh","mean"), co2_kg=("estimated_co2_kg","mean"),
        temperature_c=("temperature_c","mean"), aqi=("aqi","mean"), impact_score=("impact_score","mean")
    )
    risk_counts = df["risk_level"].value_counts().to_dict()
    return {"monthly": monthly.round(2).to_dict(orient="records"), "risk_counts": risk_counts,
            "total_records": int(len(df)), "avg_energy": round(float(df.energy_kwh.mean()),2),
            "avg_co2": round(float(df.estimated_co2_kg.mean()),2)}

@app.get("/api/environmental-data")
def environmental_data(limit: int=Query(100, ge=1, le=1000), offset: int=Query(0, ge=0),
                       user=Depends(get_current_user)):
    with get_db() as db:
        rows = db.execute("SELECT * FROM environmental_data ORDER BY date DESC LIMIT ? OFFSET ?", (limit,offset)).fetchall()
        total = db.execute("SELECT COUNT(*) c FROM environmental_data").fetchone()["c"]
    return {"items":[dict(r) for r in rows], "total":total}

@app.post("/api/environmental-data")
def add_environmental(payload: EnvironmentalCreate, user=Depends(get_current_user)):
    d = payload.model_dump()
    score = calculate_impact(d)
    d["risk_level"] = risk_from_score(score)
    with get_db() as db:
        cur = db.execute("""INSERT INTO environmental_data
        (date,location,temperature_c,humidity_pct,rainfall_mm,co2_ppm,aqi,energy_kwh,water_liters,renewable_pct,extreme_weather_index,risk_level)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        tuple(d[k] for k in ["date","location","temperature_c","humidity_pct","rainfall_mm","co2_ppm","aqi","energy_kwh","water_liters","renewable_pct","extreme_weather_index","risk_level"]))
        new_id = cur.lastrowid
    audit(user, "ADD_DATA", f"id={new_id}")
    return {"id":new_id,"risk_level":d["risk_level"],"impact_score":score}

@app.delete("/api/environmental-data/{item_id}")
def delete_environmental(item_id:int, user=Depends(get_current_user)):
    if user["role"] != "admin": raise HTTPException(403, "Admin role required")
    with get_db() as db:
        cur = db.execute("DELETE FROM environmental_data WHERE id=?", (item_id,))
    if cur.rowcount == 0: raise HTTPException(404,"Record not found")
    audit(user, "DELETE_DATA", f"id={item_id}")
    return {"deleted":True}

@app.post("/api/predict")
def make_prediction(payload: PredictionInput, user=Depends(get_current_user)):
    values = payload.model_dump()
    energy, risk = predict(values)
    with get_db() as db:
        db.execute("INSERT INTO predictions(username,predicted_energy_kwh,predicted_risk) VALUES(?,?,?)",
                   (user["username"], energy, risk))
    audit(user, "PREDICT", f"energy={energy:.2f}, risk={risk}")
    return {"predicted_energy_kwh":round(energy,2),"predicted_risk":risk}

@app.get("/api/model-metrics")
def model_metrics(user=Depends(get_current_user)):
    p = MODEL_DIR/"metrics.json"
    return json.loads(p.read_text())

@app.get("/api/anomalies")
def anomalies(user=Depends(get_current_user)):
    with get_db() as db:
        rows = db.execute("SELECT * FROM environmental_data ORDER BY date DESC LIMIT 1000").fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    ad = detect_anomalies(df)
    return {"items": ad[ad["anomaly"]].head(50).to_dict(orient="records"), "count": int(ad["anomaly"].sum())}

@app.get("/api/alerts")
def alerts(user=Depends(get_current_user)):
    with get_db() as db:
        rows = db.execute("SELECT * FROM environmental_data ORDER BY date DESC LIMIT 100").fetchall()
    out=[]
    for r in rows:
        x=dict(r); score=calculate_impact(x)
        if score>=60 or x["aqi"]>120 or x["energy_kwh"]>500 or x["extreme_weather_index"]>55:
            out.append({"date":x["date"],"location":x["location"],"risk":risk_from_score(score),
                        "impact_score":score,"message":f"Review environmental indicators for {x['location']} on {x['date']}."})
    return {"items":out[:30]}

@app.get("/api/recommendations")
def recs(user=Depends(get_current_user)):
    data = dashboard(user)
    return {"items":data["recommendations"]}

# Optional cloud/MongoDB readiness information
@app.get("/api/integrations")
def integrations(user=Depends(get_current_user)):
    from .config import MONGODB_URI
    return {"weather_provider":"offline-first demo provider",
            "mongodb_configured": bool(MONGODB_URI),
            "cloud_ready": True}

# Serve frontend build if present
frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist/"assets"), name="assets")
    @app.get("/{full_path:path}")
    def spa(full_path: str):
        candidate = frontend_dist / full_path
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(frontend_dist/"index.html")
