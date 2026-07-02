# Architecture Diagram

```mermaid
graph TD
    Client[Client / CI] --> API[FastAPI API]
    API --> Service[Evaluation Service]
    Service --> Pipeline[Evaluation Pipeline]
    Pipeline --> Registry[Provider / Judge / Metric Registry]
    Registry --> Providers[Providers]
    Registry --> Judges[Judges]
    Registry --> Metrics[Metrics]
    Pipeline --> DB[(PostgreSQL)]
    Pipeline --> Redis[(Redis)]
```

## Notes

- The API layer stays thin and delegates execution to services.
- Registries provide plugin-style discovery without manual wiring.
- Batch execution persists partial progress and failure details.
