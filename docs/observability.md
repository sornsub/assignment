# Observability

## Metrics scraping

Prometheus scrapes:

- `api:8000/metrics`
- `worker:8001/metrics`

Local scrape config lives in `prometheus/prometheus.yml`.
Kubernetes scrape config lives in `k8s/observability/prometheus.yaml`.

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

## Local access

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Default Grafana login: `admin` / `admin`

## Production note

For real production, use authentication, persistent storage, TLS, and RBAC for both Grafana and Prometheus.

Local/UAT/PROD datasources are intentionally configured as separate Prometheus endpoints.
