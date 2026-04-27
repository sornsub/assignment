import json
import logging
import os
import time
from datetime import date, datetime

from prometheus_client import start_http_server
from sqlalchemy import text

from database import SessionLocal
from observability import (
    worker_job_failures_total,
    worker_job_runs_total,
    worker_job_success_total,
    worker_last_success_timestamp,
    worker_retry_count_total,
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
WORKER_INTERVAL_SECONDS = int(os.getenv("WORKER_INTERVAL_SECONDS", "30"))
WORKER_MAX_RETRIES = int(os.getenv("WORKER_MAX_RETRIES", "3"))
WORKER_RETRY_BACKOFF_SECONDS = int(os.getenv("WORKER_RETRY_BACKOFF_SECONDS", "5"))
WORKER_METRICS_PORT = int(os.getenv("WORKER_METRICS_PORT", "8001"))


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(payload)


logger = logging.getLogger("worker")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.handlers = [handler]
logger.setLevel(LOG_LEVEL)


def ensure_table(session):
    session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS daily_records (
              id SERIAL PRIMARY KEY,
              record_date DATE NOT NULL,
              updated_at TIMESTAMP NOT NULL
            )
            """
        )
    )
    session.commit()


def ensure_seed_row(session):
    session.execute(
        text(
            """
            INSERT INTO daily_records (record_date, updated_at)
            SELECT :record_date, :updated_at
            WHERE NOT EXISTS (
              SELECT 1 FROM daily_records WHERE record_date = :record_date
            )
            """
        ),
        {"record_date": date.today(), "updated_at": datetime.utcnow()},
    )
    session.commit()


def run_once() -> None:
    session = SessionLocal()
    try:
        ensure_table(session)
        ensure_seed_row(session)
        result = session.execute(
            text(
                """
                UPDATE daily_records
                SET updated_at = :updated_at
                WHERE record_date = :record_date
                """
            ),
            {"updated_at": datetime.utcnow(), "record_date": date.today()},
        )
        session.commit()

        worker_job_runs_total.inc()
        worker_job_success_total.inc()
        worker_last_success_timestamp.set(time.time())
        logger.info(f"worker_run_success updated_rows={result.rowcount}")
    finally:
        session.close()


def run_loop() -> None:
    start_http_server(WORKER_METRICS_PORT)
    logger.info(f"worker_metrics_server_started port={WORKER_METRICS_PORT}")

    while True:
        attempt = 0
        while attempt <= WORKER_MAX_RETRIES:
            try:
                run_once()
                break
            except Exception as exc:
                attempt += 1
                worker_job_failures_total.inc()
                logger.error(f"worker_run_failed attempt={attempt} error={exc}")
                if attempt > WORKER_MAX_RETRIES:
                    logger.error("worker_retries_exhausted")
                    break
                worker_retry_count_total.inc()
                time.sleep(WORKER_RETRY_BACKOFF_SECONDS * attempt)

        time.sleep(WORKER_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_loop()
