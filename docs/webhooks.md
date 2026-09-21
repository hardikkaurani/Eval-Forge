# Eval-Forge Webhooks Guide

Eval-Forge includes a production-grade webhook dispatcher that sends real-time HTTP POST notifications to your infrastructure when evaluation jobs complete, fail, or trigger alerts.

---

## 1. Supported Event Types

| Event Type | Description | Trigger Moment |
|---|---|---|
| `evaluation.completed` | An evaluation run successfully finished scoring all test cases. | Immediately after final metrics are recorded. |
| `job.failed` | A background evaluation job failed due to worker error, model timeout, or unhandled exception. | When max retries are exhausted or fatal error occurs. |

---

## 2. Registering a Webhook

Create a webhook subscription associated with your project:

### Endpoint: `POST /api/v1/webhooks`

```bash
curl -X POST "http://localhost:8000/api/v1/webhooks" \
  -H "X-API-Key: ef_live_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "target_url": "https://api.your-company.com/evalforge/events",
    "events": ["evaluation.completed", "job.failed"],
    "is_active": true
  }'
```

### Response
```json
{
  "success": true,
  "message": "Webhook subscription created.",
  "data": {
    "id": "e4d3c2b1-5a6f-7e8d-9c0b-1a2b3c4d5e6f",
    "project_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "target_url": "https://api.your-company.com/evalforge/events",
    "events": ["evaluation.completed", "job.failed"],
    "is_active": true,
    "secret_token": "whsec_0123456789abcdef0123456789abcdef",
    "created_at": "2026-09-20T04:00:00.000Z",
    "updated_at": "2026-09-20T04:00:00.000Z"
  },
  "timestamp": "2026-09-20T04:00:00.000Z",
  "request_id": "req-abcdef12-3456"
}
```

> **Security Note:** Save the `secret_token` returned upon creation. It is used to compute HMAC signatures to verify incoming requests.

---

## 3. Webhook Request Format

When an event fires, Eval-Forge sends an HTTP POST request to your `target_url`:

### HTTP Headers
```http
POST /evalforge/events HTTP/1.1
Host: api.your-company.com
Content-Type: application/json
User-Agent: EvalForge-Webhook-Dispatcher/1.0
X-EvalForge-Event: evaluation.completed
X-EvalForge-Signature: 5d41402abc4b2a76b9719d911017c592...
```

### Request Payload Body
```json
{
  "event": "evaluation.completed",
  "subscription_id": "e4d3c2b1-5a6f-7e8d-9c0b-1a2b3c4d5e6f",
  "timestamp": 1726800000,
  "data": {
    "run_id": "99887766-5544-3322-1100-aabbccddeeff",
    "project_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Production RAG Prompt Evaluation",
    "status": "COMPLETED",
    "summary_metrics": {
      "accuracy": 0.92,
      "faithfulness": 0.88,
      "hallucination_rate": 0.04
    },
    "total_test_cases": 150,
    "passed_test_cases": 138,
    "completed_at": "2026-09-20T04:05:00.000Z"
  }
}
```

---

## 4. Verifying Signatures

To ensure payloads originate from Eval-Forge and have not been tampered with in transit:

1. Extract the `X-EvalForge-Signature` header.
2. Read the raw request body string.
3. Compute the HMAC-SHA256 hash of the raw body using your webhook's `secret_token`.
4. Perform a timing-safe equality check.

### Python Verification Example
```python
import hashlib
import hmac


def verify_evalforge_signature(
    raw_body: bytes, received_signature: str, secret_token: str
) -> bool:
    expected_signature = hmac.new(
        secret_token.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, received_signature)
```

### Node.js / TypeScript Verification Example
```typescript
import crypto from 'crypto';

export function verifyEvalForgeSignature(
  rawBody: string | Buffer,
  receivedSignature: string,
  secretToken: string,
): boolean {
  const hmac = crypto.createHmac('sha256', secretToken);
  hmac.update(rawBody);
  const expectedSignature = hmac.digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature, 'utf8'),
    Buffer.from(receivedSignature, 'utf8')
  );
}
```

---

## 5. Retries and Delivery Guarantees

- **Timeout:** 5.0 seconds per delivery attempt.
- **Max Retries:** 3 attempts with exponential backoff (1s, 2s, 4s).
- **Audit Logs:** Each delivery attempt (including status code, error message, and response latency) is recorded in the `WebhookDelivery` log and queryable via:
  ```bash
  curl -X GET "http://localhost:8000/api/v1/webhooks/YOUR_SUBSCRIPTION_UUID/deliveries" \
    -H "X-API-Key: ef_live_your_api_key_here"
  ```
- **Success Criteria:** HTTP response status code in the `2xx` range (`200`–`299`). Any `4xx`, `5xx`, or connection timeout triggers retry.
