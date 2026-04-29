from fastapi import FastAPI

app = FastAPI(
    title="PDF Extractext API",
    description="API for PDF text extraction using Clean Architecture",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    """Returns a simple health status to verify the server is running."""
    return {"status": "ok", "message": "pong"}
