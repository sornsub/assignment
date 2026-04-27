# EKS Deployment Summary

This repository includes Kubernetes manifests and Kustomize overlays for dev/uat/prod that can be applied to Amazon EKS.

## Recommended production approach

1. Use managed PostgreSQL (Amazon RDS) instead of in-cluster Postgres.
2. Push API/Worker images to ECR.
3. Replace placeholder image names in base manifests or via overlay patches.
4. Configure Ingress + TLS (ALB Ingress Controller).
5. Configure IRSA, external secrets, and restricted RBAC.

## Demo apply commands

```bash
kubectl apply -k k8s/overlays/dev
kubectl apply -f k8s/observability/
```

> PostgreSQL deployed inside Kubernetes is for local/demo only. For production, use a managed database such as Amazon RDS.
