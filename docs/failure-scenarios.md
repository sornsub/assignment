# Failure Scenarios

## 1) API crashes during peak hours

- **Symptoms:** `/health` fails, pod restarts, elevated 5xx.
- **Detection:**
  - Prometheus alerts: High API error rate / crash looping
  - Grafana API up + error rate + latency panels
- **Response:**
  1. Check pod status/logs.
  2. Roll back if tied to recent release.
  3. Scale API replicas (HPA/manual).

## 2) Worker fails and infinitely retries

- **Risk:** hot loop increases DB pressure.
- **Mitigation in this repo:** worker has `WORKER_MAX_RETRIES` and exponential-style backoff multiplier.
- **Detection:** worker failures + retries metrics, stalled alert.
- **Response:**
  1. Verify DB readiness/connectivity.
  2. Reduce worker interval temporarily.
  3. Roll back/redeploy if code regression.

## 3) Bad deployment is released

- **Symptoms:** errors spike after rollout.
- **Response:**
  1. `kubectl rollout undo` deployment.
  2. Verify health/readiness.
  3. Re-run CI checks before next release.

## 4) Kubernetes node downs

- **Symptoms:** pods evicted or pending.
- **Response:**
  1. Check node readiness/events.
  2. Reschedule pods / ensure cluster autoscaling.
  3. Confirm service endpoints recover.
