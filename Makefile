APP_NAME=fastapi-app
PORT=8000

## Install dependencies
install:
	pip install -r requirements.txt

## Run the FastAPI app locally
run:
	uvicorn main:app --reload --host 0.0.0.0 --port $(PORT)