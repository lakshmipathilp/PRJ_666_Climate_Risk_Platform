#!/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -d backend/venv ]; then python3 -m venv backend/venv; fi
source backend/venv/bin/activate
pip install -r backend/requirements.txt
if [ ! -f backend/models/energy_model.joblib ]; then
  cd backend
  python -m ml.train_model
  cd ..
fi
(cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000) &
cd frontend
npm install
npm run dev
