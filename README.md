# news-assessor-backend

A simple FastAPI backend that does the following:
- Handle the CSV file that is being uploaded from frontend.
- For each data entity in the uploaded, it tries to download the full data entity text using the attached URL.
- For each data entity, the backend encapsulate it in a prompt and send it to GPT-4o for classification using OpenAI API.
- When the response is back from GPT-4o, it stores all the classes for all the question as an excel row in an excel file attached with the data entity it self.

---

## Features
- FastAPI-based backend
- Connects to OpenAI's GPT-4o API
- Processes responses from the AI model for further use

---

## Requirements
- Python 3.9+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sipanova/news-assessor-backend.git
   cd news-assessor-backend
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate    # On macOS/Linux
   venv\Scripts\activate       # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Environment Variables

Create a `.env` file in the project root and add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

---

## Running the Application

Start the server with Uvicorn:

```bash
uvicorn main:app --reload
```

- By default, the app runs at: `http://127.0.0.1:8000`
- Add `--port` to specify a custom port if needed:
  ```bash
  uvicorn main:app --reload --port 8080
  ```

---

## Project Structure (Example)

```
news-assessor-backend/
│
├── main.py           # FastAPI app entry point
├── requirements.txt  # Dependencies
├── .env              # Environment variables
└── README.md         # This file
```

