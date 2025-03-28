import os
import re
import shutil
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
# from email_service.gmail_sender import send_email_with_attachment
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
import smtplib
from email.message import EmailMessage

# Load environment variables from a .env file
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

def send_email_with_attachment(email: str, filename: str, file_content: bytes):

    """Function to send email with an attachment (without saving the file)."""
    sender_email = os.getenv("SENDER_EMAIL")  # Replace with your email
    sender_password = os.getenv("SENDER_PASSWORD")  # Use an app password for security
    print(f'Test-4.1')
    msg = EmailMessage()
    msg["Subject"] = "CSV File Upload"
    msg["From"] = sender_email
    msg["To"] = email
    msg.set_content(f"Hello,\n\nPlease find the uploaded file: {filename} attached.\n\nBest regards,\nFastAPI App")
    print(f'Test-4.2')

    print(f'email:{email}')
    print(f'SENDER_EMAIL:{sender_email}')
    print(f'SENDER_PASSWORD:{sender_password}')


    # Attach the file directly from memory
    msg.add_attachment(file_content, maintype="application", subtype="csv", filename=filename)

    try:
        print(f'Test-4.3')

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Email sending failed: {e}")
    print(f'Test-4.4')
    


def is_valid_email(email: str) -> bool:
    """Validate email format using regex."""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email) is not None



@app.post("/process")
async def process(
    file: UploadFile = File(...),
    model: str = Form(...)
    # email: str = Form(...)
):
    


    # Validate email
    # if not is_valid_email(email):
    #     return JSONResponse(content={"error": "Invalid email format!"}, status_code=400)

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