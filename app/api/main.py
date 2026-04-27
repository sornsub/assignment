import json
import logging
from datetime import date, datetime

from fastapi import Depends, FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, DailyRecord
from observability import MetricsMiddleware

app = FastAPI(title="Agnos DevOps API")
app.add_middleware(MetricsMiddleware)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(payload)


logger = logging.getLogger("api")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.handlers = [handler]
logger.setLevel(logging.INFO)


@app.on_event("startup")
def startup() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("api_startup_complete")
    except Exception as exc:
        logger.error(f"api_startup_db_init_failed error={exc}")


@app.get("/health")
def health():
    return {"status": "ok", "service": "api"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "connected"}


@app.get("/records/today")
def records_today(db: Session = Depends(get_db)):
    today = date.today()
    rows = (
        db.query(DailyRecord)
        .filter(DailyRecord.record_date == today)
        .order_by(DailyRecord.id.asc())
        .all()
    )
    return {
        "date": today.isoformat(),
        "count": len(rows),
        "records": [
            {"id": r.id, "record_date": r.record_date.isoformat(), "updated_at": r.updated_at.isoformat()}
            for r in rows
        ],
    }


@app.get("/metrics")
def metrics():
    output = generate_latest()
    return PlainTextResponse(output.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
