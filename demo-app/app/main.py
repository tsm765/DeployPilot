import os

from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="DeployPilot Demo API",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "DeployPilot demo API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    require_config = os.getenv("REQUIRE_DEMO_CONFIG", "false").lower() == "true"
    demo_config = os.getenv("DEMO_CONFIG")

    if require_config and not demo_config:
        raise HTTPException(
            status_code=500,
            detail="Required environment variable DEMO_CONFIG is missing",
        )

    return {"status": "healthy"}


@app.get("/error")
def error() -> None:
    raise HTTPException(
        status_code=500,
        detail="Deliberate DeployPilot demo failure",
    )
