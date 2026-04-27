# Runbook

## Docker / local

```bash
docker compose up --build
docker compose ps
docker compose logs -f api
docker compose logs -f worker
```

## API checks

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/records/today
curl http://localhost:8000/metrics
```

## Worker metrics

```bash
curl http://localhost:8001/metrics
```

## Prometheus / Grafana

```bash
curl http://localhost:9090/-/healthy
# Grafana UI: http://localhost:3000
```

## Kubernetes checks

```bash
kubectl get ns
kubectl get pods -n agnos-devops
kubectl logs deploy/api -n agnos-devops
kubectl logs deploy/worker -n agnos-devops
kubectl describe hpa api -n agnos-devops
kubectl get svc -n agnos-devops
kubectl get events -n agnos-devops --sort-by=.lastTimestamp
```

## Prometheus troubleshooting queries

```promql
up
sum(rate(http_requests_total[5m]))
sum(rate(http_request_errors_total[5m]))
max(worker_last_success_timestamp)
increase(worker_job_failures_total[15m])
```
