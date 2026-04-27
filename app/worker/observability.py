from prometheus_client import Counter, Gauge

worker_last_success_timestamp = Gauge(
    "worker_last_success_timestamp",
    "Unix timestamp of last successful worker run",
)
worker_job_runs_total = Counter(
    "worker_job_runs_total",
    "Total number of successful worker job runs",
)
worker_job_success_total = Counter(
    "worker_job_success_total",
    "Compatibility metric: total successful worker runs",
)
worker_job_failures_total = Counter(
    "worker_job_failures_total",
    "Total number of worker job failures",
)
worker_retry_count_total = Counter(
    "worker_retry_count_total",
    "Total number of worker retries",
)
