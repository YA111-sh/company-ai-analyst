from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.ai.agents.workflows import run_report

app = FastAPI(title="Company AI Analyst")

CHARTS_DIR = Path(__file__).resolve().parents[1] / "ai" / "reports" / "output" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/charts", StaticFiles(directory=str(CHARTS_DIR)), name="charts")


@app.get("/api/health")
def health():
    return {"status": "ok"}


class ReportRequest(BaseModel):
    message: str


@app.post("/api/report")
async def report(req: ReportRequest):
    return await run_report(req.message)