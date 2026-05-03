from fastapi import FastAPI

app = FastAPI(title="PDF Extractext API")

@app.get("/ping")
async def ping():
    return {"message": "pong"}
