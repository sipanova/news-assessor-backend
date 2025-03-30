import os
import shutil
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
# from email_service.gmail_sender import send_email_with_attachment
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
import smtplib
from email.message import EmailMessage

load_dotenv('secrets.env')

app = FastAPI()
UPLOAD_FOLDER = "uploads"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Allow only your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)



@app.post("/process")
async def process(
    file: UploadFile = File(...),
    model: str = Form(...)
    # email: str = Form(...)
):

    # Check if the uploaded file is a CSV
    if not file.filename.endswith('.csv'):
        return JSONResponse(content={"error": "Only CSV files are allowed!"}, status_code=400)

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    # Define the path where the file will be saved
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save the uploaded file to the specified location
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        return {
            "filename": file.filename,
            "message": "This is a test message.",
            "model": model
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    



@app.get("/health")
def read_root():
    return {"health": "I'm fine habibi."}





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)