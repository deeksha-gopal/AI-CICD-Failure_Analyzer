"""FastAPI routes for log upload, analysis, history and health."""
import json
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import PurePath
from typing import Literal

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import config
from .analyzer import analyze_demo, get_excerpt
from .database import Base, engine, get_db
from .llm import analyze_with_llm
from .models import AnalysisRecord
from .redaction import redact_secrets
from .schemas import AnalysisResponse, HistoryItem


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI-Powered CI/CD Failure Analyzer",
    version="1.0.0",
    description="Local log-analysis demo with optional LLM recommendations.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "llm_enabled": bool(config.OPENAI_API_KEY), "max_log_bytes": config.MAX_LOG_BYTES}


def serialize(record: AnalysisRecord) -> AnalysisResponse:
    return AnalysisResponse(
        id=record.id,
        created_at=record.created_at,
        filename=record.filename,
        mode=record.mode,
        summary=record.summary,
        findings=json.loads(record.findings_json),
        next_steps=json.loads(record.next_steps_json),
        redacted_excerpt=record.redacted_excerpt,
        duration_ms=record.duration_ms,
    )


@app.post("/api/analyze", response_model=AnalysisResponse, status_code=201)
async def analyze(
    file: UploadFile = File(...),
    mode: Literal["demo", "llm"] = Form("demo"),
    db: Session = Depends(get_db),
):
    started = time.monotonic()
    filename = PurePath((file.filename or "pipeline.log").replace("\\", "/")).name[:160]
    if not filename.lower().endswith((".txt", ".log")):
        raise HTTPException(400, detail="Upload a .log or .txt file.")

    try:
        contents = await file.read(config.MAX_LOG_BYTES + 1)
    finally:
        await file.close()

    if len(contents) > config.MAX_LOG_BYTES:
        raise HTTPException(413, detail="Log file exceeds the 256 KiB limit.")
    try:
        raw_log = contents.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(400, detail="Please upload a UTF-8 encoded log.") from exc
    if not raw_log.strip():
        raise HTTPException(400, detail="The uploaded log file is empty.")

    redacted_log = redact_secrets(raw_log)
    if mode == "llm":
        if not config.OPENAI_API_KEY:
            raise HTTPException(400, detail="LLM mode is not configured. Add OPENAI_API_KEY to the backend environment.")
        try:
            report = await analyze_with_llm(redacted_log)
        except Exception as exc:
            # Don't leak API error details that could include internal config.
            raise HTTPException(502, detail="LLM analysis failed. Check backend configuration and try again.") from exc
    else:
        report = analyze_demo(redacted_log)

    record = AnalysisRecord(
        id=str(uuid.uuid4()), filename=filename, mode=mode,
        summary=report.summary,
        findings_json=json.dumps([f.model_dump() for f in report.findings]),
        next_steps_json=json.dumps(report.next_steps),
        redacted_excerpt=get_excerpt(redacted_log),
        duration_ms=round((time.monotonic() - started) * 1000),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return serialize(record)


@app.get("/api/history", response_model=list[HistoryItem])
def history(db: Session = Depends(get_db)):
    records = db.scalars(select(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).limit(25)).all()
    return [HistoryItem(
        id=r.id, created_at=r.created_at, filename=r.filename,
        mode=r.mode, summary=r.summary, finding_count=len(json.loads(r.findings_json)),
    ) for r in records]


@app.get("/api/history/{analysis_id}", response_model=AnalysisResponse)
def analysis_detail(analysis_id: str, db: Session = Depends(get_db)):
    record = db.get(AnalysisRecord, analysis_id)
    if record is None:
        raise HTTPException(404, detail="Analysis not found.")
    return serialize(record)
