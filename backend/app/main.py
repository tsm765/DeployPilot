from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title="DeployPilot API",
    version="0.1.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "DeployPilot backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
