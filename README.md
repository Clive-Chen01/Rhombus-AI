# Rhombus-AI---Technical-Assessment-Submission

## Deployment
### Backend
cd backend

python -m venv .venv

For Windows: .\.venv\Scripts\Activate.ps1

For Linux/MacOS: source .venv/bin/activate

pip install -r requirements.txt

### Frontend
cd frontend

npm i

## Run
### Backend
python manage.py migrate

python manage.py runserver 8000

### Frontend
npm run dev