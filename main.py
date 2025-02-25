from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def read_root():
    return {"health": "I'm fine habibi."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)