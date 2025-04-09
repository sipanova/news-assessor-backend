import os
import shutil
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, Request
from helper_function import data_pre_processing, process_by_gpt_4o, process_by_llama_mini
import time
import logging

models = ['', '']

load_dotenv('secrets.env')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Allow only your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


UPLOAD_FOLDER = "uploads"

@app.post("/process")
async def process(
    file: UploadFile = File(...),
    model: str = Form(...)
    # email: str = Form(...)
):

    # Check if the uploaded file is a CSV
    if not file.filename.endswith('.csv'):
        return JSONResponse(content={"Error": "Only CSV files are allowed!"}, status_code=400)

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    # Define the path where the file will be saved
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save the uploaded file to the specified location
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


    try:
        data_pre_processing(folder_name=UPLOAD_FOLDER, filename=file.filename)
    except Exception as e:
        return JSONResponse(content={"Error while pre-processing: ": str(e)}, status_code=500)
    

    try:
        print(f"Model: {model}")
        match model:
            case "GPT-4o":
                print("case 1")
                process_by_gpt_4o(folder_name=UPLOAD_FOLDER, filename=file.filename)
            case "Llama-3.2-3B-Instruct":
                print("case 2")
                process_by_llama_mini()
            case _:
                print("case 0")
                return JSONResponse(content={f"Unvalid model: {model}."}, status_code=500)
    except Exception as e:
        return JSONResponse(content={f"Error while processing using {model}: ": str(e)}, status_code=500)
    
    try:
        return {
            "filename": file.filename,
            "message": "This is a test message.",
            "model": model
        }
    except Exception as e:
        return JSONResponse(content={"error while returning the response: ": str(e)}, status_code=500)
    



@app.get("/")
async def read_root():
    return {"health": "I'm fine habibi."}





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)