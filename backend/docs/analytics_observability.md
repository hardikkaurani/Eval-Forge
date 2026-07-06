# EvalForge Enterprise Analytics, Reporting & Observability

This guide details the design, architecture, schemas, and endpoints of the Analytics, Reporting, and Observability platform implemented in Phase 7.

---

## 1. Architecture Overview

```mermaid
graph TD
    subgraph Raw Data Layer
        ER[Evaluation Runs] --> ERt[Evaluation Results]
        ERt --> PM[Provider Metadata]
        ERt --> RS[Rubric Scores]
    end

    subgraph Aggregation Layer
        AA[AnalyticsAggregationExecutor]
        AA -->|Queries & Computes| Raw Data Layer
    end

    subgraph Persistence Layer
        AA -->|Saves| ASN[AnalyticsSnapshot]
        AA -->|Saves| M[Metrics]
        AA -->|Saves| T[Trends]
        AA -->|Saves| L[Leaderboard]
    end

    subgraph Service Layer
        AS[AnalyticsService]
        IE[InsightsEngine]
        OS[ObservabilityService]
    end

    subgraph API Layer
        API_A[/api/v1/analytics]
        API_T[/api/v1/trends]
        API_L[/api/v1/leaderboards]
        API_I[/api/v1/insights]
        API_R[/api/v1/reports]
        API_S[/api/v1/system/metrics]
    end

    API_A --> AS
    API_T --> AS
    API_L --> AS
    API_R --> AS
    API_I --> IE
    API_S --> OS
    AS --> Persistence Layer
    IE --> Persistence Layer
    OS --> Raw Data Layer
```

---

## 2. Core Engines & Mathematics

### Enterprise Analytics Engine
- **Success Rate**: $\text{Success Rate} = \frac{\text{Passed Cases}}{\text{Total Cases}} \times 100$
- **Averages & Medians**: Computed across rubric scores and evaluation runs.
- **Standard Deviation & Percentiles**: Standard deviation is computed over all score instances. Percentiles (P95, P99) are computed for latency times using a pure Python linear interpolation method to ensure compatibility without adding heavy packages like NumPy.

### Trend Engine
- Time-series aggregation grouped by date ranges matching the selected granularity (`daily`, `weekly`, `monthly`).
- Compares performance metrics (scores, volume, latency, cost) with previous periods, returning absolute and percentage changes.

### Cost & Latency Analytics
- Tracks token usage details (prompt + completion tokens) logged by the evaluation runtime.
- Automatically estimates execution costs using default base pricing and model-specific rules for OpenAI, Google Gemini, and Anthropic Claude models.

---

## 3. Reporting & Exports
- **PDF Report Generation**: Built dynamically using `fpdf2`. Incorporates structured cover pages, professional summaries, key metric grids, and tabulated execution details.
- **CSV Export**: Compiles dataset runs, latencies, and metadata details into flat tables for external analytics integration.

---

## 4. Observability & Alerting
- **Insights Engine**: Evaluates rule-based thresholds on snapshots to auto-detect regressions (e.g., quality drops > 2%), latency spikes (> 15%), and quality improvements.
- **Observability Service**: Collects real-time CPU/Memory/Disk utilization stats, Redis connections, database connection pools, queue backlogs, and downstream provider online status.
- **Alerting System**: Auto-triggers alerts for performance degradations, logging high failure rates to alert databases.

---

## 5. REST API Specifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/analytics` | High-level aggregated evaluation stats overview |
| `POST` | `/api/v1/analytics/snapshots` | Trigger manual aggregation/refresh of snapshots |
| `POST` | `/api/v1/analytics/dashboards` | Save custom dashboard layout grids |
| `GET` | `/api/v1/analytics/dashboards` | Retrieve saved dashboard snapshots |
| `GET` | `/api/v1/trends` | Time-series trends with arbitrary date range comparisons |
| `GET` | `/api/v1/leaderboards` | Standing ranks of models/providers/datasets |
| `GET` | `/api/v1/insights` | Performance anomaly regression alerts |
| `GET` | `/api/v1/reports` | Paginated and filtered lists of reports |
| `POST` | `/api/v1/reports/generate` | Generate PDF/CSV files in background |
| `GET` | `/api/v1/reports/{id}/download` | Download compiled report files |
| `GET` | `/api/v1/system/metrics` | System health observability stats |
