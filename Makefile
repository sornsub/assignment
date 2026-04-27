.PHONY: up down test api-test validate-json

up:
	docker compose up --build

down:
	docker compose down -v

test:
	cd app/api && pytest -q

validate-json:
	python -m json.tool grafana/dashboards/agnos-overview.json > /tmp/agnos-dashboard.json
