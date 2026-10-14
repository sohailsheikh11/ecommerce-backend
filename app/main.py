
from fastapi import FastAPI

app = FastAPI(
    title="E-commerce Backend API",
    description="A REST API for an online shopping platform.",
    version="1.0.0",
)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "message": "E-commerce API is running",
    }

