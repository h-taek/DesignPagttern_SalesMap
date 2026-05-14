from fastapi import FastAPI

app = FastAPI(title="SalesMap Backend", version="0.0.1")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}
