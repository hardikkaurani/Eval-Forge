# Operations Manual

This manual details operational monitoring, telemetry collection, health checking, and system administration routines.

---

## 1. Health Checks & Probes

| Endpoint | Target | Behavior |
|----------|--------|----------|
| `/api/v1/health` | Health Check | Validates internal status of Postgres & Redis. |
| `/api/v1/ready` | Readiness Probe | Returns HTTP 503 if critical dependencies are down. |
| `/api/v1/live` | Liveness Probe | Confirms FastAPI container event loop is active. |

---

## 2. Telemetry & Metrics Exporters

* **Prometheus Metrics**: Exposed on `/api/v1/metrics`. Collects request count counters and latency histograms.
* **Structured Logging**: Log entries are serialized in JSON format containing a unique correlation ID (`request_id`) bound via ContextVars to trace execution paths across handlers, services, and workers.
* **OpenTelemetry integration**: Configure OTLP exporters in environment to forward traces to Jaeger, Zipkin, or OpenTelemetry collectors.
