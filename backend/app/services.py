from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from .config import EMISSION_FACTOR_KG_PER_KWH

def calculate_impact(row):
    # Project-specific, transparent score (not an international standard).
    temp_component = np.clip((float(row["temperature_c"]) - 25) / 10, 0, 1)
    co2_component = np.clip((float(row["co2_ppm"]) - 400) / 180, 0, 1)
    aqi_component = np.clip(float(row["aqi"]) / 200, 0, 1)
    extreme_component = np.clip(float(row["extreme_weather_index"]) / 100, 0, 1)
    energy_component = np.clip(float(row["energy_kwh"]) / 650, 0, 1)
    risk = 100 * (0.25*temp_component + 0.25*co2_component + 0.20*aqi_component +
                  0.15*extreme_component + 0.15*energy_component)
    return round(float(risk), 1)

def risk_from_score(score):
    if score < 35: return "Low"
    if score < 60: return "Moderate"
    if score < 80: return "High"
    return "Critical"

def recommendations(latest):
    recs = []
    if latest["energy_kwh"] > 500:
        recs.append(("High", "Energy consumption is above the demonstration threshold. Review high-load equipment and peak-period usage."))
    if latest["co2_ppm"] > 470:
        recs.append(("High", "CO₂ concentration is elevated relative to the dataset baseline. Investigate energy-intensive activities and ventilation conditions."))
    if latest["aqi"] > 120:
        recs.append(("High", "Air-quality index is elevated. Review local pollution sources and consider exposure-reduction measures."))
    if latest["renewable_pct"] < 20:
        recs.append(("Medium", "Renewable energy share is low. Evaluate feasible renewable sourcing or efficiency measures."))
    if latest["water_liters"] > 3000:
        recs.append(("Medium", "Water consumption is high. Review water-intensive processes and possible leakage or wastage."))
    if latest["extreme_weather_index"] > 55:
        recs.append(("Critical", "Environmental risk indicators are elevated. Review preparedness and contingency measures."))
    if not recs:
        recs.append(("Low", "Current indicators are within the project's normal monitoring ranges. Continue tracking trends."))
    return recs

def detect_anomalies(df):
    x = df[["energy_kwh","co2_ppm","aqi"]].astype(float)
    model = IsolationForest(contamination=0.03, random_state=666)
    pred = model.fit_predict(x)
    df = df.copy()
    df["anomaly"] = np.where(pred == -1, True, False)
    return df
