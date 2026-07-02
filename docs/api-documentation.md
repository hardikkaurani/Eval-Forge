# API Documentation

The evaluation API is exposed under `/api/v1`.

## Core endpoints

- `POST /api/v1/evaluations`
- `GET /api/v1/evaluations`
- `GET /api/v1/evaluations/{id}`
- `DELETE /api/v1/evaluations/{id}`
- `POST /api/v1/evaluations/batch`

## Catalog endpoints

- `GET /api/v1/providers`
- `GET /api/v1/judges`
- `GET /api/v1/rubrics`

## Response format

All routes return the standard EvalForge response envelope:

- `success`
- `message`
- `data`
- `timestamp`
- `request_id`

## Notes

- Validation errors are returned in the same envelope with `success=false`.
- Batch runs are persisted before execution so progress is observable even during partial failures.
