import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
DB_PATH = BASE_DIR / "climate.db"

SECRET_KEY = os.getenv("SECRET_KEY", "PRJ666-change-this-secret-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Configurable demonstration emission factor. Replace with a region/provider-specific
# factor for real deployments.
EMISSION_FACTOR_KG_PER_KWH = float(os.getenv("EMISSION_FACTOR_KG_PER_KWH", "0.82"))

MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "prj666_climate")
