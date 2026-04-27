# Security Notes

## Non-root containers

- API and Worker images run as non-root user (`appuser`) in Dockerfiles.

## Secrets handling

- Secrets are not hardcoded in code.
- Local defaults come from `.env` / `.env.example` for demo only.
- Kubernetes includes `secret.yaml.example`; create real `Secret` outside git.

## Image scanning

- CI runs Trivy image scans after Docker builds.

## Resource limits

- Kubernetes deployments define requests/limits for API, Worker, and Postgres.

## Network exposure

- API and observability services are ClusterIP by default in Kubernetes manifests.
- Grafana has comments for LoadBalancer only when demo external access is needed.
