@echo off
setlocal
cd /d "%~dp0"
if not exist backend\venv (
  py -m venv backend\venv
)
call backend\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
if not exist backend\models\energy_model.joblib (
  cd backend
  python -m ml.train_model
  cd ..
)
start "PRJ666 Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
cd frontend
if not exist node_modules npm install
npm run dev
