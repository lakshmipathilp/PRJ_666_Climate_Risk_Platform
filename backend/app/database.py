import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'analyst',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS environmental_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    location TEXT NOT NULL,
    temperature_c REAL NOT NULL,
    humidity_pct REAL NOT NULL,
    rainfall_mm REAL NOT NULL,
    co2_ppm REAL NOT NULL,
    aqi REAL NOT NULL,
    energy_kwh REAL NOT NULL,
    water_liters REAL NOT NULL,
    renewable_pct REAL NOT NULL,
    extreme_weather_index REAL NOT NULL,
    risk_level TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    action TEXT NOT NULL,
    detail TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    predicted_energy_kwh REAL,
    predicted_risk TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript(SCHEMA)

def seed_data():
    from pathlib import Path
    import pandas as pd
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) c FROM environmental_data").fetchone()["c"]
        if count:
            return
        csv_path = Path(__file__).resolve().parents[1] / "data" / "climate_data.csv"
        df = pd.read_csv(csv_path)
        cols = ["date","location","temperature_c","humidity_pct","rainfall_mm","co2_ppm",
                "aqi","energy_kwh","water_liters","renewable_pct","extreme_weather_index","risk_level"]
        rows = [tuple(x) for x in df[cols].itertuples(index=False, name=None)]
        conn.executemany("""INSERT INTO environmental_data
            (date,location,temperature_c,humidity_pct,rainfall_mm,co2_ppm,aqi,energy_kwh,
             water_liters,renewable_pct,extreme_weather_index,risk_level)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", rows)
