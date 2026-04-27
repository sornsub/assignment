# Agnos DevOps Assignment (Environment-Separated Local Demo)

This repository delivers an assignment-focused, production-minded DevOps setup for a minimal API + worker system, emphasizing reliability, security, CI/CD, and observability.

> ⚠️ Included secret values are demo-only for local assignment use. Do **not** use them in real environments.

## Architecture Overview

Core components:
- **API service (FastAPI)**
  - `/health` for liveness status
  - `/ready` for readiness/database connectivity
  - `/metrics` for Prometheus metrics
  - `/records/today` for inspecting current-day records
- **Worker service (Python process)**
  - Periodically updates `updated_at` for records with today's `record_date`
  - Exposes worker metrics on port `8001`
- **PostgreSQL** (local/demo persistence)
- **Prometheus + Grafana** (metrics, dashboards, alerts)
- **Kubernetes manifests** with base + env overlays (`dev`, `uat`, `prod`)
- **GitHub Actions CI/CD** for lint/test/build/scan/push and mocked deploy

Environment separation:
- Workloads run in dedicated namespaces:
  - `agnos-devops-dev`
  - `agnos-devops-uat`
  - `agnos-devops-prod`
- Monitoring stack runs centrally in:
  - `agnos-monitoring`

## Local Docker Compose Setup

Use environment-specific files:

```bash
# Dev
docker compose --env-file .env.dev up -d --build

# UAT
docker compose --env-file .env.uat up -d --build

# Prod demo
docker compose --env-file .env.prod up -d --build
```

Stop and clean:

```bash
docker compose down -v
```

Useful local endpoints:
- API: http://localhost:8000
- Worker metrics: http://localhost:8001/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Quick checks:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/records/today
curl http://localhost:8000/metrics
curl http://localhost:8001/metrics
```

## Kubernetes Deployment Instructions

Apply app overlays:

```bash
kubectl apply -k k8s/overlays/dev
kubectl apply -k k8s/overlays/uat
kubectl apply -k k8s/overlays/prod
```

Apply observability stack:

```bash
kubectl create ns agnos-monitoring
kubectl apply -f k8s/observability/
```

Validate rendered manifests before apply:

```bash
kubectl apply --dry-run=client -k k8s/overlays/dev
kubectl apply --dry-run=client -k k8s/overlays/uat
kubectl apply --dry-run=client -k k8s/overlays/prod
kubectl apply --dry-run=client -f k8s/observability/
```

## Usage Instructions

Common checks:

```bash
kubectl get pods -n agnos-devops-dev
kubectl get pods -n agnos-devops-uat
kubectl get pods -n agnos-devops-prod
kubectl get pods -n agnos-monitoring
kubectl describe hpa api -n agnos-devops-dev
```

Port-forward examples:

```bash
kubectl -n agnos-devops-dev port-forward svc/api 8000:8000
kubectl -n agnos-monitoring port-forward svc/grafana 3000:3000
kubectl -n agnos-monitoring port-forward svc/prometheus 9090:9090
```

## Monitoring Access Instructions

- Prometheus UI: `http://localhost:9090`
- Grafana UI: `http://localhost:3000`
- Dashboard: **Agnos DevOps Overview** (auto-provisioned)

Key observed signals:
- API request volume, error rate, p95 latency
- Worker last success timestamp, success/failure/retry counts
- Pod restart trends (when kube-state metrics are available)

## CI/CD Flow Explanation

Workflow: `.github/workflows/ci-cd.yaml`

On push to `dev`, `uat`, `main` (or on PR):
1. Determine target environment name
2. Run Python syntax lint and API unit tests
3. Build API and worker images for scan
4. Run Trivy scans
5. On non-PR events: login to GHCR and push both versioned and `<env>-latest` tags
6. Execute mocked deploy step (prints intended deployment artifacts)

Tagging strategy:
- Immutable: `<env>-<github_run_number>-<short_sha>`
- Moving: `<env>-latest`

## Rollback Instructions

### Kubernetes rollback

```bash
kubectl rollout history deploy/api -n agnos-devops-prod
kubectl rollout undo deploy/api -n agnos-devops-prod
kubectl rollout undo deploy/worker -n agnos-devops-prod
```

### Image rollback

Re-point overlay image tags from `*-latest` to a known-good immutable tag and re-apply:

```bash
kubectl apply -k k8s/overlays/prod
```

## Failure Scenario Handling

### 1) API crashes during peak hours
- Check `kubectl get pods`, restart counts, and API logs.
- Use Grafana + Prometheus alerts for high error/crash-looping behavior.
- Scale API via HPA bounds or manual replicas while mitigating incident.
- Roll back recent deployment if regression suspected.

### 2) Worker fails and infinitely retries
- Worker includes bounded retries (`WORKER_MAX_RETRIES`) and backoff (`WORKER_RETRY_BACKOFF_SECONDS`).
- Inspect worker failure/retry metrics and logs.
- Confirm PostgreSQL connectivity/readiness.
- Roll back/redeploy worker when failure source is code/config regression.

### 3) Bad deployment is released
- Identify increase in error rate/latency after rollout.
- Run `kubectl rollout undo` for affected deployment(s).
- Verify `/health` and `/ready` recover and alert state clears.

### 4) Kubernetes node goes down
- Check node readiness and pod rescheduling (`kubectl get nodes`, `kubectl get events`).
- Confirm new pods become Ready on healthy nodes.
- Validate service endpoints and API/worker metrics recovery.

## Security Notes

- API/worker containers run as non-root (`appuser`).
- Secrets are injected from env/Secret manifests, not hardcoded in source.
- Trivy image scanning is included in CI.
- Kubernetes manifests define resource requests/limits.
- Services are ClusterIP by default for internal communication.
- For real production, replace demo secrets with a proper secret manager and enforce RBAC/NetworkPolicy.
