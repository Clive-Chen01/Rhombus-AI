# Rhombus-AI---Technical-Assessment-Submission
Using Django and React. Supported by Ollama.

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

### Ollama
Download Ollama from https://ollama.com/ and run it

Choose a model(In this project, I use gpt-oss:120b from Ollama Cloud, so I get an API Key from my account.)

## Run
### Backend
cd backend

python manage.py runserver 8000

### Frontend
cd frontend

npm run dev
