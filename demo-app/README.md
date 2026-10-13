# DeployPilot Demo App

A small FastAPI service that acts as the deployable workload for DeployPilot.

## Run locally

From this directory, install the dependencies and start the development server:

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The service provides:

- `GET /` — a welcome message
- `GET /health` — healthy by default; returns HTTP 500 when `REQUIRE_DEMO_CONFIG=true` and `DEMO_CONFIG` is missing or empty
- `GET /error` — deliberately returns HTTP 500

To try the configuration failure, set `REQUIRE_DEMO_CONFIG=true` without setting
`DEMO_CONFIG`, then request `/health`. Set `DEMO_CONFIG` to a nonempty value to
restore the healthy response.

## Tests

From this directory, run:

```bash
python -m pytest
```
