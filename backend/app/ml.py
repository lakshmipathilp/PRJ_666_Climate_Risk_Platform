from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report
from .config import DATA_DIR, MODEL_DIR

FEATURES = ["temperature_c","humidity_pct","rainfall_mm","co2_ppm","aqi","water_liters","renewable_pct","extreme_weather_index"]
TARGET = "energy_kwh"

def train_models():
    MODEL_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_DIR / "climate_data.csv")
    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=666)
    rf = RandomForestRegressor(n_estimators=250, random_state=666, n_jobs=-1)
    rf.fit(X_train, y_train)
    pred = rf.predict(X_test)
    metrics = {
        "mae": round(float(mean_absolute_error(y_test, pred)), 3),
        "rmse": round(float(mean_squared_error(y_test, pred)**0.5), 3),
        "r2": round(float(r2_score(y_test, pred)), 4)
    }
    joblib.dump(rf, MODEL_DIR / "energy_model.joblib")

    # Risk classifier trained on the dataset's transparent risk labels.
    Xr = df[FEATURES]
    yr = df["risk_level"]
    Xtr, Xte, ytr, yte = train_test_split(Xr, yr, test_size=0.2, random_state=666, stratify=yr)
    clf = RandomForestClassifier(n_estimators=250, random_state=666, n_jobs=-1)
    clf.fit(Xtr, ytr)
    rp = clf.predict(Xte)
    rmetrics = {"accuracy": round(float(accuracy_score(yte, rp)), 4)}
    joblib.dump(clf, MODEL_DIR / "risk_model.joblib")

    (MODEL_DIR / "metrics.json").write_text(__import__("json").dumps({
        "energy_model": metrics,
        "risk_model": rmetrics,
        "features": FEATURES,
        "note": "Metrics are calculated on the included synthetic demonstration dataset."
    }, indent=2))
    return metrics, rmetrics

def ensure_models():
    MODEL_DIR.mkdir(exist_ok=True)
    if not (MODEL_DIR/"energy_model.joblib").exists() or not (MODEL_DIR/"risk_model.joblib").exists():
        train_models()

def predict(values):
    ensure_models()
    energy_model = joblib.load(MODEL_DIR / "energy_model.joblib")
    risk_model = joblib.load(MODEL_DIR / "risk_model.joblib")
    x = pd.DataFrame([values])[FEATURES]
    energy = float(energy_model.predict(x)[0])
    risk = str(risk_model.predict(x)[0])
    return energy, risk
