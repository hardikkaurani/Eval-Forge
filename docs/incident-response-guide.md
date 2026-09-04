# Incident Response Guide

This guide outlines standard operating procedures (SOPs) for responding to system degradation, outages, or security incidents.

---

## 1. Severity Classifications

- **Sev 1 (Critical)**: Platform completely down, security breach, or data loss.
- **Sev 2 (Major)**: Degraded evaluation performance, worker pool down, or high API latencies (> 2s).
- **Sev 3 (Minor)**: Partial UI failure or analytics metrics delay.

---

## 2. Standard Operating Procedures (SOP)

### A. High Latency Spikes or Database Overload

1. Inspect the `/api/v1/metrics` endpoint and database connection pool logs.
2. Scale backend API pods horizontally.
3. Identify long-running SQL queries using `pg_stat_activity` and verify cache hit rates.

### B. Redis Cache Outage or Worker Disconnections

1. Confirm Redis memory usage. Evict expired keys or scale memory limits if needed.
2. Restart worker pods to re-initialize task queue listeners.
3. Fallback cache will automatically handle requests using in-memory local dict buffers.
