# Observability

## Metrics scraping

Prometheus scrapes:

- `api:8000/metrics`
- `worker:8001/metrics`

Local scrape config lives in `prometheus/prometheus.yml`.
Kubernetes scrape config lives in `k8s/observability/prometheus.yaml`.

## Alert rules and Alertmanager

Alert rules live in:

- Local: `prometheus/prometheus-rules.yml`
- Kubernetes: `k8s/observability/prometheus-rules.yaml`

Alertmanager config lives in:

- Local: `alertmanager/alertmanager.yml`
- Kubernetes: `k8s/observability/alertmanager.yaml`

Current alerts include:

- `HighApiErrorRate` (warning): API error ratio over 5% for 5m.
- `HighApiLatencyP95` (warning): API p95 latency over 750ms for 10m.
- `WorkerStalled` (critical): worker has no successful execution for 15m.
- `WorkerFailuresHigh` (warning): worker failures increase above threshold.
- `CrashLoopingPods` (warning): pod/container restart rate indicates crash looping.
- `ApiTargetDown` (critical): API scrape target unavailable.
- `WorkerTargetDown` (critical): worker scrape target unavailable.
- `ScrapeTargetDownByEnv` (warning, Kubernetes): env-labeled target unavailable.

## Grafana provisioning

Grafana provisioning files:

- Datasources: `grafana/provisioning/datasources/datasources.yaml`
- Dashboard provider: `grafana/provisioning/dashboards/dashboards.yaml`
- Dashboard JSON: `grafana/dashboards/agnos-overview.json`

Datasources created automatically:

- Prometheus Local
- Prometheus UAT
- Prometheus PROD

Prometheus Local is default.

## Switching dashboard datasource

Dashboard variable `DS_PROMETHEUS` lets you switch between Local/UAT/PROD using Grafana's top dropdown.
All panels are configured to use `${DS_PROMETHEUS}`.

## Local start and access

Start observability stack locally:

```bash
make alerts-local
# or full stack:
make up
```

Access:

- Prometheus: http://localhost:9090
- Prometheus alerts page: http://localhost:9090/alerts
- Alertmanager: http://localhost:9093
- Grafana: http://localhost:3000
- Default Grafana login: `admin` / `admin`

## How to test target-down alerts

1. Start local stack: `make up`
2. Stop API or worker:
   - `docker compose stop api`
   - `docker compose stop worker`
3. Wait 2-3 minutes for `ApiTargetDown` or `WorkerTargetDown` to fire.
4. Check Prometheus alerts page and Alertmanager UI.
5. Restart target:
   - `docker compose start api`
   - `docker compose start worker`

## Kubernetes demo alerting

Deploy monitoring including Alertmanager:

```bash
make alerts-k8s
```

Prometheus sends alerts to:

- `alertmanager.agnos-monitoring.svc.cluster.local:9093`

## Suggested production receivers

For production, replace demo webhook receiver with managed/on-call integrations:

- Slack
- Email/SMTP
- PagerDuty
- Opsgenie

## Validation commands

```bash
make validate-alerts
docker compose config
kubectl kustomize k8s/overlays/dev
kubectl kustomize k8s/overlays/uat
kubectl kustomize k8s/overlays/prod
kubectl apply --dry-run=client -f k8s/observability/
```

`make validate-alerts` runs YAML checks and `promtool` checks if `promtool` is installed.

## Production note

For real production, use authentication, persistent storage, TLS, and RBAC for Grafana, Prometheus, and Alertmanager.

Local/UAT/PROD datasources are intentionally configured as separate Prometheus endpoints.
