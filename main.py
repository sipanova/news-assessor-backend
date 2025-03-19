import os
import re
import shutil
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()
UPLOAD_FOLDER = "uploads"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Allow only your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/health")
def read_root():
    return {"health": "I'm fine habibi."}


def is_valid_email(email: str) -> bool:
    """Validate email format using regex."""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email) is not None

@app.post("/process")
async def upload_file(
    file: UploadFile = File(...),
    model: str = Form(...),
    email: str = Form(...)
):
    # Validate email
    if not is_valid_email(email):
        return JSONResponse(content={"error": "Invalid email format!"}, status_code=400)

    # Check if the uploaded file is a CSV
    if not file.filename.endswith('.csv'):
        return JSONResponse(content={"error": "Only CSV files are allowed!"}, status_code=400)

    # Define the path where the file will be saved
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save the uploaded file to the specified location
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "message": "File uploaded successfully!",
        "model": model,
        "email": email
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)