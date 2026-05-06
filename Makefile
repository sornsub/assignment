.PHONY: \
	up down test validate-json validate-alerts alerts-local alerts-k8s \
	compose-dev compose-uat compose-prod \
	deploy-dev deploy-uat deploy-prod deploy-monitoring \
	pods-dev pods-uat pods-prod pods-monitoring \
	api-dev api-uat api-prod grafana prometheus

up:
	docker compose --env-file .env.dev up -d --build

down:
	docker compose down -v

test:
	cd app/api && pytest -q

validate-json:
	python -m json.tool grafana/dashboards/agnos-overview.json > /tmp/agnos-dashboard.json

validate-alerts:
	python -c "import yaml; yaml.safe_load(open('prometheus/prometheus.yml')); yaml.safe_load(open('prometheus/prometheus-rules.yml')); yaml.safe_load(open('alertmanager/alertmanager.yml')); yaml.safe_load_all(open('k8s/observability/prometheus.yaml')); yaml.safe_load(open('k8s/observability/prometheus-rules.yaml')); list(yaml.safe_load_all(open('k8s/observability/alertmanager.yaml'))); print('YAML validation passed')"
	@if command -v promtool >/dev/null 2>&1; then \
		promtool check config prometheus/prometheus.yml && \
		promtool check rules prometheus/prometheus-rules.yml; \
	else \
		echo "promtool not installed; run 'promtool check config prometheus/prometheus.yml' and 'promtool check rules prometheus/prometheus-rules.yml' manually."; \
	fi

alerts-local:
	docker compose --env-file .env.dev up -d prometheus alertmanager

alerts-k8s:
	kubectl apply -f k8s/observability/prometheus-rules.yaml
	kubectl apply -f k8s/observability/alertmanager.yaml
	kubectl apply -f k8s/observability/prometheus.yaml

compose-dev:
	docker compose --env-file .env.dev up -d --build

compose-uat:
	docker compose --env-file .env.uat up -d --build

compose-prod:
	docker compose --env-file .env.prod up -d --build

deploy-dev:
	kubectl apply -k k8s/overlays/dev

deploy-uat:
	kubectl apply -k k8s/overlays/uat

deploy-prod:
	kubectl apply -k k8s/overlays/prod

deploy-monitoring:
	kubectl apply -f k8s/observability/

pods-dev:
	kubectl get pods -n agnos-devops-dev

pods-uat:
	kubectl get pods -n agnos-devops-uat

pods-prod:
	kubectl get pods -n agnos-devops-prod

pods-monitoring:
	kubectl get pods -n agnos-monitoring

api-dev:
	kubectl -n agnos-devops-dev port-forward svc/api 8000:8000

api-uat:
	kubectl -n agnos-devops-uat port-forward svc/api 8001:8000

api-prod:
	kubectl -n agnos-devops-prod port-forward svc/api 8002:8000

grafana:
	kubectl -n agnos-monitoring port-forward svc/grafana 3000:3000

prometheus:
	kubectl -n agnos-monitoring port-forward svc/prometheus 9090:9090
