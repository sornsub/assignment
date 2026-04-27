# Architecture

## Overview

This repository contains a production-minded but local/demo-friendly DevOps assignment:

- **API service (FastAPI)**
  - health/readiness endpoints
  - PostgreSQL reads (`/records/today`)
  - Prometheus metrics (`/metrics`)
- **Worker service (Python)**
  - periodic update job for today's records in PostgreSQL
  - retry with max retry + backoff
  - Prometheus metrics on port `8001`
- **PostgreSQL** for local/demo persistence
- **Prometheus + Grafana** for monitoring/alerting and dashboards
- **Kubernetes manifests** with base + overlays (dev/uat/prod)
- **GitHub Actions CI/CD** for lint, tests, builds, scan, mocked deploy

## Data flow

1. API receives traffic and records request metrics.
2. Worker periodically updates rows in `daily_records` for current date.
3. Prometheus scrapes `/metrics` from API and worker.
4. Grafana loads provisioned datasources + dashboard and supports datasource switching across Local/UAT/PROD.
