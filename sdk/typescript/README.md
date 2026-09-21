# Eval-Forge TypeScript SDK (`@evalforge/sdk`)

Official TypeScript / JavaScript client library for the [Eval-Forge](https://github.com/hardikkaurani/Eval-Forge) AI evaluation and LLM observability platform.

---

## Installation

```bash
npm install @evalforge/sdk
```

Or using Yarn / pnpm:
```bash
yarn add @evalforge/sdk
# or
pnpm add @evalforge/sdk
```

---

## Authentication

Set your API key via the `EVALFORGE_API_KEY` environment variable:

```bash
export EVALFORGE_API_KEY="ef_live_your_api_key_here"
export EVALFORGE_BASE_URL="http://localhost:8000"  # Optional, defaults to http://localhost:8000
```

Or provide it directly to the constructor:

```typescript
import { EvalForge } from '@evalforge/sdk';

const client = new EvalForge({
  apiKey: 'ef_live_your_api_key_here',
  baseUrl: 'http://localhost:8000', // optional
  timeoutMs: 30000,                 // optional
  maxRetries: 3,                    // optional
});
```

---

## Quickstart

```typescript
import { EvalForge } from '@evalforge/sdk';

async function run() {
  const client = new EvalForge();

  // 1. Create or retrieve a project
  const project = await client.projects.create(
    'Customer Support Bot Evaluation',
    'Automated accuracy and hallucination benchmark'
  );
  console.log(`Created Project: ${project.name} (${project.id})`);

  // 2. Launch an evaluation run
  const evalRun = await client.evaluations.create(
    project.id,
    'Support Prompt v2.1 Benchmark',
    [
      {
        input: 'How do I change my billing email?',
        actual_output: 'Navigate to Account Settings > Billing to update your email address.',
        expected_output: 'Go to Settings > Billing and enter the new email.',
      },
    ],
    ['accuracy', 'semantic_similarity', 'hallucination']
  );
  console.log(`Launched Evaluation Run: ID=${evalRun.id}, Status=${evalRun.status}`);

  // 3. Inspect job status
  if (evalRun.job_id) {
    const job = await client.jobs.get(evalRun.job_id);
    console.log(`Job Progress: ${job.progress_pct}% (${job.status})`);
  }
}

run().catch(console.error);
```

---

## Error Handling

All SDK errors inherit from `EvalForgeError`:

```typescript
import {
  EvalForge,
  AuthenticationError,
  NotFoundError,
  RateLimitError,
  APIError,
} from '@evalforge/sdk';

try {
  const client = new EvalForge();
  await client.projects.get('invalid-uuid');
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error('Invalid or missing API key:', error.message);
  } else if (error instanceof NotFoundError) {
    console.error('Target resource does not exist:', error.message);
  } else if (error instanceof RateLimitError) {
    console.error('Rate limit reached:', error.message);
  } else if (error instanceof APIError) {
    console.error(`API Error (${error.statusCode}):`, error.message);
  }
}
```

---

## License

MIT
