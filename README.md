# Agnos DevOps Assignment (Environment-Separated Local Demo)

This project runs the same app stack in **dev**, **uat**, and **prod (demo)** modes for local Docker Compose and Kubernetes/Minikube, while keeping monitoring centralized.

> ⚠️ Included secrets are for local demo/assignment use only. Do **not** commit real production secrets.
> In real systems, use External Secrets, Sealed Secrets, SOPS, Vault, or a cloud secret manager.

## Architecture Summary

- App workloads run in separate namespaces:
  - `agnos-devops-dev`
  - `agnos-devops-uat`
  - `agnos-devops-prod`
- Monitoring runs centrally in:
  - `agnos-monitoring`
- Prometheus scrapes app services across namespaces via Kubernetes DNS.
- Grafana uses one Prometheus datasource and supports filtering by `env` label.
- Config is separated per environment via overlay ConfigMap patches.
- Secrets are separated per environment via overlay Secret manifests (demo-only).
- Images are separated by moving tags:
  - `dev-latest`, `uat-latest`, `prod-latest`
- CI/CD keeps immutable tags for traceability/rollback:
  - `<env>-<github_run_number>-<short_sha>`

## Docker Compose

Create/select env file and run:

- Dev:
  ```bash
  docker compose --env-file .env.dev up -d --build
  ```
- UAT:
  ```bash
  docker compose --env-file .env.uat up -d --build
  ```
- Prod demo:
  ```bash
  docker compose --env-file .env.prod up -d --build
  ```

Endpoints:
- API: http://localhost:8000
- Worker metrics: http://localhost:8001/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Health checks:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## Kubernetes / Minikube

Deploy each environment:

```bash
kubectl apply -k k8s/overlays/dev
kubectl apply -k k8s/overlays/uat
kubectl apply -k k8s/overlays/prod
```

Deploy centralized monitoring:

```bash
kubectl apply -f k8s/observability/
```

Checks:

```bash
kubectl get pods -n agnos-devops-dev
kubectl get pods -n agnos-devops-uat
kubectl get pods -n agnos-devops-prod
kubectl get pods -n agnos-monitoring
kubectl get svc -n agnos-monitoring
```

Port-forward:

```bash
kubectl -n agnos-devops-dev port-forward svc/api 8000:8000
kubectl -n agnos-devops-uat port-forward svc/api 8001:8000
kubectl -n agnos-devops-prod port-forward svc/api 8002:8000
kubectl -n agnos-monitoring port-forward svc/grafana 3000:3000
kubectl -n agnos-monitoring port-forward svc/prometheus 9090:9090
```

## Notes

- `k8s/base` is environment-neutral (no hard-coded namespace).
- Overlays control env-specific namespace, secret values, config values, image tags, and scaling.
- `latest` tags are kept for local demo convenience; immutable tags remain for CI/CD traceability.
