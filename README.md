# Agnos DevOps Assignment (Production-minded, Local/Demo Runnable)

## 1) Architecture overview

This repository contains:
- **FastAPI API service** with health/readiness/metrics/data endpoints.
- **Python worker service** that updates today's PostgreSQL records periodically.
- **PostgreSQL** for local/demo persistence.
- **Prometheus + Grafana** with auto-provisioned datasources and dashboard.
- **Kubernetes manifests** (base + dev/uat/prod overlays with Kustomize).
- **GitHub Actions CI/CD** (lint, tests, image build, Trivy scan, mocked deploy).

> PostgreSQL deployed inside Kubernetes is for local/demo only. For production, use a managed database such as Amazon RDS.

## 2) Repository structure

```text
app/
  api/
  worker/
k8s/
  base/
  overlays/{dev,uat,prod}/
  observability/
grafana/
prometheus/
docs/
.github/workflows/
```

## 3) Local setup instructions

1. Copy env file:
   ```bash
   cp .env.example .env
   ```
2. Start everything:
   ```bash
   docker compose up --build
   ```

## 4) Docker Compose usage

Main services exposed locally:
- API: http://localhost:8000
- Worker metrics: http://localhost:8001/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Default Grafana login:
- Username: `admin`
- Password: `admin`

Verification commands:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/records/today
curl http://localhost:8000/metrics
curl http://localhost:8001/metrics
```

## 5) Kubernetes deployment instructions

Create ns :
```bash
kubectl create ns agnos-devops
```

Create secret (demo):
```bash
kubectl apply -f k8s/base/secret.yaml.example
```

Deploy app (dev overlay):
```bash
kubectl apply -k k8s/overlays/dev
```

Deploy observability:
```bash
kubectl apply -f k8s/observability/
```

Also available:
```bash
kubectl apply -k k8s/overlays/uat
kubectl apply -k k8s/overlays/prod
```

## 6) EKS deployment summary

See `docs/eks-deployment.md` for EKS-oriented guidance: using ECR, RDS, ingress/TLS, RBAC, IRSA, and external secrets.

## 7) CI/CD explanation

Workflow: `.github/workflows/ci-cd.yaml`
- Lint (Python compile check)
- Unit tests (`pytest`)
- Docker Buildx image builds
- Trivy image scan
- Mocked deploy step (no real cloud credentials required)

## 8) Monitoring explanation

- Prometheus scrapes API/Worker metrics.
- Grafana auto-provisions datasources:
  - Prometheus Local
  - Prometheus UAT
  - Prometheus PROD
- Dashboard `Agnos DevOps Overview` supports datasource switching via `DS_PROMETHEUS`.

See `docs/observability.md`.

## 9) Failure scenario summary

Covered in `docs/failure-scenarios.md`:
- API crashes during peak
- Worker failure/retry behavior
- Bad deployment rollback
- Kubernetes node failure handling

## 10) Download repository as ZIP from GitHub

1. Open the repository page on GitHub.
2. Click **Code**.
3. Click **Download ZIP**.
4. Unzip locally and run `docker compose up --build`.
