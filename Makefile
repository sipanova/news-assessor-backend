APP_NAME=fastapi-app
PORT=8000
VENV=venv-backend
PYTHON=python

.PHONY: venv install run clean

## Create virtual environment if it doesn't exist
venv:
	@if not exist "$(VENV)" $(PYTHON) -m venv $(VENV)

## Install dependencies
install: 
	PowerShell -ExecutionPolicy Bypass -Command "$(VENV)\\Scripts\\Activate.ps1; $(VENV)\\Scripts\\python.exe -m pip install --upgrade pip; pip install -r requirements.txt"

## Run the FastAPI app locally
run: 
	PowerShell -ExecutionPolicy Bypass -Command "$(VENV)\\Scripts\\Activate.ps1; uvicorn main:app --reload --host 127.0.0.1 --port=$(PORT)"


build-run: venv install run

## Clean up the virtual environment
clean:
	rmdir /s /q $(VENV)
