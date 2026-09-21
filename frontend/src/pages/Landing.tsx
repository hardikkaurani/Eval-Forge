import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Code2,
  Copy,
  Cpu,
  CreditCard,
  Database,
  DollarSign,
  ExternalLink,
  FileText,
  FlaskConical,
  Gauge,
  Github,
  Layers,
  Linkedin,
  Menu,
  MessageSquare,
  Play,
  RotateCcw,
  ShieldCheck,
  Sliders,
  Sparkles,
  Terminal,
  Twitter,
  X,
  Zap,
} from 'lucide-react';
import { useConnection } from '../context/ConnectionContext';
import { ThemeControl } from '../layouts/WorkspaceShell';

interface CapabilityItem {
  num: string;
  title: string;
  tagline: string;
  desc: string;
  icon: typeof Database;
  highlights: string[];
  specs: { label: string; value: string }[];
  codeLanguage: string;
  codeSnippet: string;
  actionLabel: string;
  actionRoute: string;
}

const CAPABILITIES: CapabilityItem[] = [
  {
    num: '01',
    title: 'Versioned Datasets',
    tagline: 'Deterministic ground-truth benchmarks and schema-validated dataset governance.',
    desc: 'Upload CSV, JSON, and JSONL datasets with validated schemas, golden references, and schema mapping.',
    icon: Database,
    highlights: [
      'Strict JSON Schema & Pydantic validation on ingest',
      'SHA-256 cryptographic dataset hashing & snapshot immutability',
      'Golden reference sets with paired expected ground-truth answers',
      'Automated schema diff detection and migration tracking',
    ],
    specs: [
      { label: 'Supported Formats', value: 'CSV, JSON, JSONL, Parquet' },
      { label: 'Schema Enforcement', value: 'Pydantic v2 + JSON Schema Draft 7' },
      { label: 'Versioning', value: 'SHA-256 Content-Addressed Hash' },
      { label: 'Max Dataset Size', value: '500MB per batch (Multi-chunk streaming)' },
    ],
    codeLanguage: 'python',
    codeSnippet: `from evalforge import EvalClient

client = EvalClient(api_key="ef_live_...")

# Register and validate a versioned golden benchmark dataset
dataset = client.datasets.create(
    name="golden-support-benchmarks-v2",
    format="jsonl",
    file_path="./data/golden_eval.jsonl",
    schema_validation={
        "query": str,
        "expected_answer": str,
        "context_documents": list[str]
    },
    golden_truth_enabled=True
)

print(f"Dataset registered: {dataset.id} (v{dataset.version})")`,
    actionLabel: 'Manage Datasets in Workspace',
    actionRoute: '/projects',
  },
  {
    num: '02',
    title: 'G-Eval & LLM Judges',
    tagline: 'Multi-criteria rubric execution with chain-of-thought verification.',
    desc: 'Run multi-criteria rubrics with chain-of-thought explanations. Quantify alignment, coherence, and accuracy.',
    icon: FlaskConical,
    highlights: [
      'Multi-criteria weighted rubrics for semantic quality and alignment',
      'Chain-of-thought (CoT) reasoning traces captured for every score',
      'Inter-annotator agreement metrics (Cohen’s Kappa) against human labels',
      'Support for GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, and Llama 3',
    ],
    specs: [
      { label: 'Scoring Scales', value: 'Continuous (0.0 - 1.0) or Discrete (1 - 5)' },
      { label: 'Judge Architectures', value: 'OpenAI, Anthropic, Google Gemini, Ollama' },
      { label: 'Reasoning Mode', value: 'Full CoT Explanations with Token Logs' },
      { label: 'Calibration', value: 'Automatic prompt temperature dampening (0.0)' },
    ],
    codeLanguage: 'python',
    codeSnippet: `# Execute G-Eval multi-criteria rubric evaluation
evaluation = client.evaluations.create(
    dataset_id="ds_customer_v2",
    judge_model="gpt-4o",
    temperature=0.0,
    rubric={
        "coherence": {"weight": 0.30, "criteria": "Logical flow and structural clarity"},
        "factuality": {"weight": 0.40, "criteria": "Zero hallucinations against golden context"},
        "safety": {"weight": 0.30, "criteria": "Strict compliance with safety guardrails"}
    },
    require_reasoning_trace=True
)

summary = evaluation.wait_for_completion()
print(f"Overall Score: {summary.aggregate_score:.2f} / 1.0")`,
    actionLabel: 'Launch LLM Evaluation',
    actionRoute: '/projects',
  },
  {
    num: '03',
    title: 'RAG Faithfulness',
    tagline: 'Rigorous triad evaluation for retrieval-augmented generation pipelines.',
    desc: 'Measure retrieval precision, context recall, and output groundedness against your reference knowledge base.',
    icon: Layers,
    highlights: [
      'RAG Triad metrics: Context Relevance, Groundedness, Answer Relevance',
      'Sentence-level citation grounding with source context attribution',
      'Vector retrieval precision and recall against indexed document chunks',
      'Automated hallucination flags for ungrounded synthetic claims',
    ],
    specs: [
      { label: 'Triad Formulation', value: 'Context Precision, Context Recall, Faithfulness' },
      { label: 'Attribution Granularity', value: 'Sentence-level span highlighting' },
      { label: 'Context Windows', value: 'Up to 128k token context chunks evaluated' },
      { label: 'Scoring Engine', value: 'Token overlap + Semantic embedding similarity' },
    ],
    codeLanguage: 'python',
    codeSnippet: `# Evaluate RAG Triad: Context Recall, Precision & Faithfulness
rag_metrics = client.metrics.rag_triad(
    query="What is the cluster failover SLA for Enterprise tier?",
    retrieved_chunks=[
        "Enterprise clusters provide automated multi-region failover under 90s."
    ],
    generated_response="Enterprise tier automated failover completes within 90 seconds.",
    strict_citation=True
)

print(f"Faithfulness Score: {rag_metrics.faithfulness}")        # 1.00
print(f"Context Recall:     {rag_metrics.context_recall}")      # 1.00
print(f"Hallucination Risk: {rag_metrics.hallucination_score}") # 0.00`,
    actionLabel: 'Run RAG Benchmark',
    actionRoute: '/projects',
  },
  {
    num: '04',
    title: 'Deep Analytics & Drift',
    tagline: 'Continuous score distributions, regression slicing, and drift telemetry.',
    desc: 'Observe score distributions, monitor model regressions, detect failure slices, and export audit trails.',
    icon: BarChart3,
    highlights: [
      'Continuous score distribution comparison (Wasserstein distance & KS-test)',
      'Automated failure slicing to identify weak prompt patterns or topics',
      'Exportable audit trails in signed PDF, CSV, and machine-readable JSON',
      'Configurable CI/CD threshold gates to block regression pull requests',
    ],
    specs: [
      { label: 'Statistical Tests', value: 'Two-Sample Kolmogorov-Smirnov, p < 0.05' },
      { label: 'Regression Slicing', value: 'Automated clustering by prompt length & topic' },
      { label: 'Telemetry Export', value: 'Prometheus metrics, Datadog, Signed JSON' },
      { label: 'Alerting', value: 'Slack, Webhooks, PagerDuty, GitHub PR status' },
    ],
    codeLanguage: 'python',
    codeSnippet: `# Statistical regression detection across model versions
comparison = client.analytics.compare(
    baseline_run_id="eval_run_gpt4_base",
    candidate_run_id="eval_run_gpt4o_rc1",
    p_value_threshold=0.05
)

if comparison.has_regression:
    print(f"ALERT: Regression detected in slice '{comparison.regressed_slice}'")
    print(f"Delta: {comparison.score_delta:.3f} (p={comparison.p_value})")
else:
    print("Zero statistically significant regression. Safe to deploy.")`,
    actionLabel: 'Explore Analytics Dashboard',
    actionRoute: '/overview',
  },
  {
    num: '05',
    title: 'Distributed Async Jobs',
    tagline: 'High-throughput Celery and Redis queuing for massive evaluation suites.',
    desc: 'Decoupled Celery and Redis queuing handles high-volume asynchronous batch evaluation workloads.',
    icon: Zap,
    highlights: [
      'Decoupled Redis job broker with Celery distributed worker pools',
      'Adaptive token-bucket rate limiting across multiple LLM providers',
      'Fault-tolerant execution with checkpointing and automatic retry on 429/5xx',
      'Server-Sent Events (SSE) live progress streams and webhook dispatch',
    ],
    specs: [
      { label: 'Queue Engine', value: 'Redis 7.x + Celery Distributed Worker Fleet' },
      { label: 'Concurrency', value: 'Scalable up to 256 concurrent evaluator threads' },
      { label: 'Backoff Strategy', value: 'Exponential jittered retry on provider 429' },
      { label: 'Streaming', value: 'Real-time SSE token stream & state updates' },
    ],
    codeLanguage: 'python',
    codeSnippet: `# Dispatch high-throughput async evaluation job
job = client.jobs.submit(
    dataset_id="ds_100k_multilingual",
    evaluation_suite="production_regression_gate",
    concurrency=64,
    webhook_url="https://api.internal.com/evals/complete",
    retry_policy={"max_retries": 3, "backoff_multiplier": 1.5}
)

print(f"Dispatched Job ID: {job.id}")
# Listen to live progress via Server-Sent Events (SSE)
for event in client.jobs.stream_progress(job.id):
    print(f"Progress: {event.completed_samples}/{event.total_samples} ({event.percent}%)")`,
    actionLabel: 'Inspect Queue & System Health',
    actionRoute: '/settings/system',
  },
  {
    num: '06',
    title: 'Developer Platform',
    tagline: 'CLI, Model Context Protocol (MCP), webhooks, and multi-language SDKs.',
    desc: 'Command-line CLI, Model Context Protocol (MCP), webhooks, and SDKs in Python, TypeScript, Java, and Go.',
    icon: Terminal,
    highlights: [
      'Native Anthropic Model Context Protocol (MCP) server integration',
      'Lightweight CLI for running evaluations directly in local terminal or CI/CD',
      'Official SDKs in Python, TypeScript/Node.js, Go, and Java',
      'Fully typed OpenAPI 3.1 REST API with scoped API keys and RBAC',
    ],
    specs: [
      { label: 'Protocol Support', value: 'Anthropic Model Context Protocol (MCP) + REST' },
      { label: 'CLI Tooling', value: 'evalforge CLI with terminal TUI & exit codes' },
      { label: 'CI/CD Support', value: 'GitHub Actions, GitLab CI, CircleCI native actions' },
      { label: 'API Specs', value: 'OpenAPI 3.1 / Swagger documentation' },
    ],
    codeLanguage: 'bash',
    codeSnippet: `# Install EvalForge CLI
pip install evalforge-cli

# Run evaluation suite as a GitHub Actions CI test gate
evalforge run \\
  --project prj_live_alpha \\
  --suite golden-coherence-v2 \\
  --min-score 0.88 \\
  --output ./eval-report.json

# Exit code 0 if score >= 0.88, non-zero if regression detected!`,
    actionLabel: 'View Developer SDK & CLI Guide',
    actionRoute: '/developer',
  },
];

interface ArchitectureItem {
  name: string;
  role: string;
  badge: string;
  icon: typeof Database;
  overview: string;
  highlights: string[];
  specs: { label: string; value: string }[];
  codeLanguage: string;
  codeSnippet: string;
  actionLabel: string;
  actionRoute: string;
}

const ARCHITECTURE_STACK: ArchitectureItem[] = [
  {
    name: 'FastAPI',
    role: 'Backend Core',
    badge: 'Python 3.12',
    icon: Terminal,
    overview:
      'Asynchronous ASGI application server providing high-throughput REST endpoints, streaming Server-Sent Events (SSE), and Pydantic v2 data validation.',
    highlights: [
      'Pydantic v2 high-speed serialization and request schema validation',
      'Asynchronous concurrency with uvloop and asyncpg connection pooling',
      'Automated OpenAPI 3.1 interactive API documentation generation',
      'Cryptographically signed JWT and API key authentication middleware',
    ],
    specs: [
      { label: 'Runtime', value: 'Python 3.12 / ASGI uvloop' },
      { label: 'Validation Engine', value: 'Pydantic v2.8+' },
      { label: 'Protocols', value: 'REST, Server-Sent Events (SSE), Webhooks' },
      { label: 'Documentation', value: '/docs (Swagger UI), /redoc' },
    ],
    codeLanguage: 'python',
    codeSnippet: `from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="EvalForge API", version="1.0.0")

class EvaluationRequest(BaseModel):
    dataset_id: str = Field(..., description="Target dataset identifier")
    judge_model: str = Field("gpt-4o", description="Evaluation LLM judge")
    temperature: float = Field(0.0, ge=0.0, le=1.0)

@app.post("/api/v1/evaluations/run")
async def run_evaluation(req: EvaluationRequest):
    # Dispatches asynchronous task to distributed Celery worker queue
    job = celery_app.send_task("tasks.evaluate", args=[req.model_dump()])
    return {"job_id": job.id, "status": "queued"}`,
    actionLabel: 'Inspect API & Developer Specs',
    actionRoute: '/developer',
  },
  {
    name: 'PostgreSQL',
    role: 'State Store',
    badge: 'SQLAlchemy',
    icon: Database,
    overview:
      'ACID-compliant relational database storing evaluation datasets, rubrics, versioned runs, telemetry logs, and fine-grained access control policies.',
    highlights: [
      'SQLAlchemy 2.0 async ORM engine with robust connection pooling',
      'Alembic declarative migration scripts for zero-downtime schema evolution',
      'Native JSONB columns for flexible, indexed LLM rubric verdicts',
      'Composite indexes optimized for sub-millisecond evaluation queries',
    ],
    specs: [
      { label: 'Database Engine', value: 'PostgreSQL 16.x' },
      { label: 'ORM Framework', value: 'SQLAlchemy 2.0 (Async Engine)' },
      { label: 'Migration Engine', value: 'Alembic 1.13+' },
      { label: 'Driver Layer', value: 'asyncpg (Native C-extensions)' },
    ],
    codeLanguage: 'python',
    codeSnippet: `from sqlalchemy import Column, String, Float, JSON, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class EvaluationRecord(Base):
    __tablename__ = "evaluation_records"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), nullable=False, index=True)
    dataset_id = Column(String(36), nullable=False)
    aggregate_score = Column(Float, nullable=False)
    rubric_scores = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())`,
    actionLabel: 'Explore Project Datasets',
    actionRoute: '/projects',
  },
  {
    name: 'Redis',
    role: 'Queue & Cache',
    badge: 'In-Memory',
    icon: Zap,
    overview:
      'Ultra low-latency in-memory data store acting as the Celery task broker, token-bucket rate limiter, and cache layer for benchmark evaluations.',
    highlights: [
      'Sub-millisecond latency message broker for asynchronous job queuing',
      'Token-bucket sliding window rate limiting per LLM model provider',
      'Real-time Pub/Sub channels broadcasting evaluation progress events',
      'Transparent response caching for idempotent evaluation rubrics',
    ],
    specs: [
      { label: 'Cache Engine', value: 'Redis 7.2 In-Memory Key-Value' },
      { label: 'Broker Role', value: 'Celery Task Queue & Pub/Sub' },
      { label: 'Persistence', value: 'AOF (Append Only File) + RDB Snapshots' },
      { label: 'Rate Limiter', value: 'Sliding-window token bucket script' },
    ],
    codeLanguage: 'python',
    codeSnippet: `import redis.asyncio as redis

redis_pool = redis.ConnectionPool.from_url("redis://localhost:6379/0")
client = redis.Redis(connection_pool=redis_pool)

async def acquire_provider_slot(provider: str, max_tps: int = 50) -> bool:
    """Atomic rate limit slot reservation using Redis sliding window."""
    key = f"rate_limit:{provider}"
    current_count = await client.incr(key)
    if current_count == 1:
        await client.expire(key, 1) # 1 second window
    return current_count <= max_tps`,
    actionLabel: 'Inspect System Health & Queues',
    actionRoute: '/settings/system',
  },
  {
    name: 'Celery',
    role: 'Async Workers',
    badge: 'Distributed',
    icon: Cpu,
    overview:
      'Distributed task execution cluster that runs evaluation batches in parallel across worker nodes with auto-retry on LLM provider throttling.',
    highlights: [
      'Horizontally scalable containerized Celery worker fleet',
      'Automatic exponential backoff on HTTP 429/503 provider errors',
      'Dedicated task prioritization queues for golden benchmark runs',
      'Granular checkpointing enabling instant resume on worker interruption',
    ],
    specs: [
      { label: 'Worker Engine', value: 'Celery 5.4.x' },
      { label: 'Execution Pool', value: 'Prefork / Gevent concurrency' },
      { label: 'Result Backend', value: 'Redis 7.x + PostgreSQL' },
      { label: 'Scheduler', value: 'Celery Beat for recurring regressions' },
    ],
    codeLanguage: 'python',
    codeSnippet: `from celery import Celery

celery_app = Celery("evalforge", broker="redis://localhost:6379/0")

@celery_app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=2,
    autoretry_for=(Exception,),
    retry_backoff=True
)
def evaluate_sample_batch(self, sample_ids: list[str]):
    results = [run_rubric_eval(sid) for sid in sample_ids]
    self.update_state(state="PROGRESS", meta={"processed": len(results)})
    return results`,
    actionLabel: 'Manage Scheduled Benchmark Jobs',
    actionRoute: '/scheduled-jobs',
  },
  {
    name: 'React 18',
    role: 'Web Interface',
    badge: 'TypeScript',
    icon: Code2,
    overview:
      'Modern, highly responsive enterprise frontend engineered with TypeScript, TanStack Query, TailwindCSS, and accessible design system components.',
    highlights: [
      'React 18 concurrent features with route-level lazy loading',
      'TanStack Query v5 for intelligent server-state caching & sync',
      'Strict WCAG AA accessibility with keyboard navigation & dialog focus',
      'Editorial styling system with seamless light/dark theme transitions',
    ],
    specs: [
      { label: 'Frontend Library', value: 'React 18.3' },
      { label: 'Build Tool', value: 'Vite 6.x (Instant HMR & Optimized Bundles)' },
      { label: 'Type Safety', value: 'TypeScript 5.x Strict Mode' },
      { label: 'Routing & State', value: 'React Router v6 + TanStack Query v5' },
    ],
    codeLanguage: 'tsx',
    codeSnippet: `import { useQuery } from '@tanstack/react-query';
import { api } from '../services/client';

export function LiveEvaluationMonitor({ jobId }: { jobId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => api.getJobStatus(jobId),
    refetchInterval: (query) => (query.state.data?.status === 'running' ? 2000 : false),
  });

  return (
    <div className="p-4 rounded-xl border border-[var(--border)]">
      <h3>Status: {data?.status ?? 'Initializing'}</h3>
      <span>Processed: {data?.completed ?? 0} / {data?.total ?? 0}</span>
    </div>
  );
}`,
    actionLabel: 'Explore Workspace Dashboard',
    actionRoute: '/overview',
  },
  {
    name: 'Stripe',
    role: 'Billing & RBAC',
    badge: 'Enterprise',
    icon: CreditCard,
    overview:
      'Enterprise payment and entitlement gateway managing subscription tiers, metered LLM token usage, team seats, and cryptographically verified webhooks.',
    highlights: [
      'Automated metered usage billing for high-volume batch evaluations',
      'Self-serve Stripe Customer Portal for invoices and plan upgrades',
      'Cryptographic HMAC SHA-256 webhook signature verification',
      'Enterprise team seats with role-based access control (RBAC)',
    ],
    specs: [
      { label: 'Payment Gateway', value: 'Stripe API 2024-06 (PCI DSS Level 1)' },
      { label: 'Webhook Verification', value: 'HMAC SHA-256 Signature Auth' },
      { label: 'Billing Tiers', value: 'Free, Pro, Team & Custom Enterprise' },
      { label: 'Invoicing', value: 'Automated tax and multi-currency support' },
    ],
    codeLanguage: 'python',
    codeSnippet: `import stripe
from fastapi import Request, HTTPException, Header

stripe.api_key = "sk_live_..."

@app.post("/api/v1/billing/stripe-webhook")
async def handle_stripe_event(request: Request, stripe_signature: str = Header(...)):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "customer.subscription.updated":
        await update_workspace_entitlements(event["data"]["object"])
    return {"status": "success"}`,
    actionLabel: 'Manage Billing & Subscriptions',
    actionRoute: '/settings/billing',
  },
];

interface JudgeModelBenchmark {
  id: string;
  name: string;
  provider: string;
  badge: string;
  faithfulness: number;
  cotReasoning: number;
  hallucinationDetection: number;
  latencyMs: number;
  costPer10k: string;
  contextWindow: string;
  verdictSample: {
    question: string;
    verdict: string;
    score: string;
    reasoning: string;
  };
}

const JUDGE_BENCHMARKS: JudgeModelBenchmark[] = [
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'OpenAI',
    badge: 'Industry Standard',
    faithfulness: 98.4,
    cotReasoning: 97.5,
    hallucinationDetection: 99.0,
    latencyMs: 240,
    costPer10k: '$1.40',
    contextWindow: '128k tokens',
    verdictSample: {
      question: 'What is the enterprise cluster failover SLA window?',
      verdict: 'PASS — High Groundedness',
      score: '1.00 / 1.00',
      reasoning:
        'The candidate output asserts a 90-second SLA, which directly matches the retrieved infrastructure telemetry document (Section 4.1). Zero unsupported assertions or hallucinations detected.',
    },
  },
  {
    id: 'claude-3-5-sonnet',
    name: 'Claude 3.5 Sonnet',
    provider: 'Anthropic',
    badge: 'Top Reasoning & Code',
    faithfulness: 98.8,
    cotReasoning: 98.2,
    hallucinationDetection: 99.3,
    latencyMs: 280,
    costPer10k: '$1.50',
    contextWindow: '200k tokens',
    verdictSample: {
      question: 'Does the customer support response violate compliance policies?',
      verdict: 'FLAGGED — Policy Adherence',
      score: '0.98 / 1.00',
      reasoning:
        'The response correctly identifies that unencrypted credential logging violates SOC-2 Type II protocols and refrains from generating insecure configuration templates.',
    },
  },
  {
    id: 'gemini-1-5-pro',
    name: 'Gemini 1.5 Pro',
    provider: 'Google DeepMind',
    badge: 'Massive Context Leader',
    faithfulness: 97.6,
    cotReasoning: 96.8,
    hallucinationDetection: 98.4,
    latencyMs: 310,
    costPer10k: '$1.25',
    contextWindow: '2,000,000 tokens',
    verdictSample: {
      question: 'Cross-reference user query across 50-page technical manual.',
      verdict: 'PASS — Comprehensive Context Retrieval',
      score: '0.97 / 1.00',
      reasoning:
        'Successfully retrieved and cross-correlated data points across multi-chapter specifications with perfect needle-in-a-haystack recall.',
    },
  },
  {
    id: 'llama-3-3-70b',
    name: 'Llama 3.3 70B',
    provider: 'Meta / Self-Hosted',
    badge: 'Open Weights Sovereign',
    faithfulness: 96.2,
    cotReasoning: 95.1,
    hallucinationDetection: 97.0,
    latencyMs: 160,
    costPer10k: '$0.35',
    contextWindow: '128k tokens',
    verdictSample: {
      question: 'Perform local air-gapped rubric verification.',
      verdict: 'PASS — Sovereign Execution',
      score: '0.95 / 1.00',
      reasoning:
        'Completed local evaluation without egressing data outside the customer VPC. Strict adherence to numeric rubric scoring boundaries.',
    },
  },
  {
    id: 'deepseek-r1',
    name: 'DeepSeek-R1',
    provider: 'DeepSeek',
    badge: 'Deep Reasoning Engine',
    faithfulness: 98.1,
    cotReasoning: 98.9,
    hallucinationDetection: 98.6,
    latencyMs: 420,
    costPer10k: '$0.85',
    contextWindow: '64k tokens',
    verdictSample: {
      question: 'Evaluate logical consistency of complex mathematical deduction.',
      verdict: 'PASS — Formal Verification',
      score: '1.00 / 1.00',
      reasoning:
        'Traced mathematical transformations through 7 sequential deduction steps, validating each algebraic derivation with formal chain-of-thought logic.',
    },
  },
];

interface LegalDoc {
  id: string;
  title: string;
  badge: string;
  lastUpdated: string;
  content: { heading: string; text: string }[];
}

const TESTIMONIALS = [
  {
    name: 'Sarah W.',
    role: 'Staff ML Infrastructure Engineer',
    company: 'FinCognitive',
    avatar:
      'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80',
    quote:
      'EvalForge reduced our LLM regression cycle from 3 days to 45 seconds. The deterministic G-Eval scoring gave our risk and compliance teams the statistical evidence needed to authorize production deployment.',
  },
  {
    name: 'David C.',
    role: 'Head of AI Engineering',
    company: 'Synthetix Cloud',
    avatar:
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
    quote:
      'The sovereign judge matrix is remarkable. We benchmark GPT-4o, Claude 3.5, and self-hosted DeepSeek models side-by-side on the exact same golden test suite with zero vendor lock-in.',
  },
  {
    name: 'Amina M.',
    role: 'Lead Clinical NLP Scientist',
    company: 'HealthVector',
    avatar:
      'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80',
    quote:
      'RAG grounding and context precision metrics caught subtle hallucinations in our clinical query pipelines that standard unit tests missed. The MCP server integrated into our developer workflow effortlessly.',
  },
  {
    name: 'Marcus V.',
    role: 'Principal Solutions Architect',
    company: 'ScaleOps Enterprise',
    avatar:
      'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80',
    quote:
      'High-throughput async execution allowed us to process over 250,000 synthetic test cases per week across our continuous CI/CD GitHub Actions pipelines without degrading developer velocity.',
  },
];

const FAQ_ITEMS = [
  {
    q: 'How does EvalForge evaluate LLM outputs with deterministic precision?',
    a: 'EvalForge utilizes multi-judge consensus with calibrated prompt rubrics (G-Eval methodology), reference-guided ground-truth embeddings, and exact-match deterministic assertions. Judges are executed with zero temperature (T=0) and fixed random seeds to guarantee repeatable, empirically verifiable pass/fail scoring across pipeline revisions.',
  },
  {
    q: 'Can EvalForge be deployed in an air-gapped private VPC or on-premise Kubernetes cluster?',
    a: 'Yes. EvalForge provides a containerized architecture (Docker Compose & Helm charts) engineered for zero external telemetry. You can run evaluations against self-hosted open-weights models (such as Llama 3.3, Mistral, and DeepSeek-R1) via vLLM or Ollama without any data ever leaving your private security perimeter.',
  },
  {
    q: 'How does the Sovereign Judge Matrix prevent evaluation bias and self-preference?',
    a: 'Empirical research shows frontier LLMs exhibit self-preference bias when judging their own generations. EvalForge mitigates this through cross-model judging matrices (e.g., Anthropic Claude evaluating OpenAI GPT outputs and vice-versa) paired with randomized sample permutation and position-bias correction algorithms.',
  },
  {
    q: 'How does EvalForge integrate with modern CI/CD pipelines?',
    a: 'EvalForge offers first-class integrations: a native GitHub Actions action, a lightweight terminal CLI (`evalforge run`), and webhook notifications. If evaluation regressions drop below your defined pass-rate threshold, the CI step exits with a non-zero code, preventing faulty model updates or degraded prompts from reaching staging or production.',
  },
  {
    q: 'What evaluation metrics are supported out of the box?',
    a: 'EvalForge provides built-in evaluators for the RAG Triad (Factual Faithfulness, Answer Relevancy, Context Precision), Chain-of-Thought (CoT) reasoning rubrics, semantic embedding similarity, toxicity and prompt-injection safety filters, latency percentiles (P50/P95/P99), and custom Python assertion scripts.',
  },
  {
    q: 'Is EvalForge open-source and free for commercial development?',
    a: 'The core EvalForge evaluation runtime, CLI, client SDKs, and Model Context Protocol (MCP) server are 100% open-source under the permissive MIT License. You have complete freedom to audit, modify, and self-host within your commercial products and services.',
  },
];

const LEGAL_DOCS: Record<string, LegalDoc> = {
  privacy: {
    id: 'privacy',
    title: 'Enterprise Privacy & Zero Data Retention Policy',
    badge: 'Security & Compliance',
    lastUpdated: 'September 2026',
    content: [
      {
        heading: '1. Zero-Retention Principle',
        text: 'EvalForge is engineered from the ground up for strict confidentiality. Prompt datasets, generated model responses, and computed evaluation artifacts are never stored in external persistent databases unless explicitly configured in self-hosted workspaces.',
      },
      {
        heading: '2. Local & Air-Gapped Execution',
        text: 'For sovereign enterprise deployments, all evaluation calculations, embeddings, and metric scoring run on your private infrastructure (Docker, Kubernetes, or air-gapped clusters). No telemetry or test samples leave your VPC.',
      },
      {
        heading: '3. No Model Training on Customer Data',
        text: 'Under no circumstances are customer prompts, golden test suites, or evaluation results used for training foundation models or third-party AI systems.',
      },
      {
        heading: '4. Cryptographic Encryption Standards',
        text: 'All data transmitted between your local client, terminal CLI, and evaluation server is secured via TLS 1.3. Evaluation artifacts at rest in your workspace database utilize AES-256 encryption.',
      },
    ],
  },
  security: {
    id: 'security',
    title: 'Security Architecture & Vulnerability Disclosure',
    badge: 'Enterprise Trust',
    lastUpdated: 'September 2026',
    content: [
      {
        heading: '1. Role-Based Access Control (RBAC)',
        text: 'EvalForge enforces granular permission scopes across workspaces, projects, and evaluation jobs. Scoped API keys ensure CI/CD runner environments have least-privilege access.',
      },
      {
        heading: '2. Sandbox Container Isolation',
        text: 'Custom Python validation scripts and user-defined rubric code execute in strictly isolated, sandboxed runtime environments without network egress privileges, mitigating arbitrary code execution risks.',
      },
      {
        heading: '3. SOC2 Type II & HIPAA Alignment',
        text: 'Our architectural primitives adhere to SOC2 Type II trust principles and HIPAA compliance standards for automated machine learning governance.',
      },
      {
        heading: '4. Responsible Disclosure Program',
        text: 'If you identify a security vulnerability in the EvalForge repository, please report it privately to security@evalforge.ai or via GitHub Private Vulnerability Reporting.',
      },
    ],
  },
  terms: {
    id: 'terms',
    title: 'Terms of Infrastructure & Open Source Licensing',
    badge: 'Legal Agreement',
    lastUpdated: 'September 2026',
    content: [
      {
        heading: '1. Permissive MIT Open Source Core',
        text: 'EvalForge core software, including the CLI, client SDKs, evaluation engine, and Model Context Protocol (MCP) server, is distributed under the permissive MIT License. You are free to inspect, modify, and distribute the codebase.',
      },
      {
        heading: '2. Commercial & Private Self-Hosting',
        text: 'Organizations are fully authorized to deploy EvalForge within commercial applications, internal CI/CD pipelines, and proprietary enterprise platforms without licensing fees or recurring runtime royalties.',
      },
      {
        heading: '3. Service Level Expectations',
        text: 'For enterprise cluster deployments with dedicated support contracts, EvalForge guarantees 99.98% platform availability and 24/7 incident escalation SLAs.',
      },
    ],
  },
  whitepaper: {
    id: 'whitepaper',
    title: 'Technical Whitepaper: Deterministic AI Verification',
    badge: 'Research Publication',
    lastUpdated: 'September 2026',
    content: [
      {
        heading: 'Abstract',
        text: 'Modern generative AI pipelines suffer from non-deterministic variance and heuristic evaluation blindspots. EvalForge introduces a mathematical framework uniting G-Eval chain-of-thought rubrics with empirical reference distributions and position-bias correction.',
      },
      {
        heading: 'Multi-Judge Consensus Matrix',
        text: 'By evaluating candidate generations across orthogonal frontier judges (e.g. Claude 3.5 Sonnet, GPT-4o, and DeepSeek-R1) under zero-temperature deterministic parameters, inter-annotator agreement (Cohen’s Kappa) increases from 0.62 to 0.94.',
      },
      {
        heading: 'Statistical Power in Regression Testing',
        text: 'Using bootstrap confidence intervals and McNemar hypothesis testing on golden benchmark datasets, EvalForge guarantees that model improvements are statistically significant at p < 0.01.',
      },
    ],
  },
};

export default function Landing() {
  const { connected } = useConnection();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeCodeTab, setActiveCodeTab] = useState<'python' | 'cli' | 'rest' | 'simulator'>(
    'python'
  );
  const [simSuite, setSimSuite] = useState<'rag' | 'rubric' | 'safety'>('rag');
  const [simRunning, setSimRunning] = useState(false);
  const [simCompleted, setSimCompleted] = useState(false);
  const [simLogs, setSimLogs] = useState<string[]>([
    'Click "Run Live Simulation" to execute evaluation against sovereign judge.',
  ]);
  const [terminalCodeCopied, setTerminalCodeCopied] = useState(false);
  const [selectedJudge, setSelectedJudge] = useState<string>('gpt-4o');

  const [selectedCap, setSelectedCap] = useState<CapabilityItem | null>(null);
  const [modalTab, setModalTab] = useState<'specs' | 'code'>('specs');
  const [copiedCode, setCopiedCode] = useState(false);

  const [selectedTech, setSelectedTech] = useState<ArchitectureItem | null>(null);
  const [techModalTab, setTechModalTab] = useState<'specs' | 'code'>('specs');
  const [copiedTechCode, setCopiedTechCode] = useState(false);

  const [platformModalOpen, setPlatformModalOpen] = useState(false);
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);
  const [activeDocModal, setActiveDocModal] = useState<LegalDoc | null>(null);
  const [copiedBadge, setCopiedBadge] = useState<string | null>(null);

  const handleCopyBadge = (cmd: string, key: string) => {
    navigator.clipboard.writeText(cmd);
    setCopiedBadge(key);
    setTimeout(() => setCopiedBadge(null), 2000);
  };

  const runSimulation = (suiteKey: 'rag' | 'rubric' | 'safety' = simSuite) => {
    setActiveCodeTab('simulator');
    setSimRunning(true);
    setSimCompleted(false);
    setSimLogs(['[0.00s] Initializing sovereign evaluation runner session...']);

    setTimeout(() => {
      setSimLogs((prev) => [
        ...prev,
        `[0.12s] Pulling '${suiteKey.toUpperCase()}' test suite (10 golden benchmark samples)... OK`,
      ]);
    }, 280);

    setTimeout(() => {
      setSimLogs((prev) => [
        ...prev,
        `[0.26s] Connecting to judge model 'gpt-4o' (temperature=0.0, seed=42)... CONNECTED`,
      ]);
    }, 550);

    setTimeout(() => {
      setSimLogs((prev) => [
        ...prev,
        `[0.42s] Evaluating context precision, ground-truth alignment, and hallucination flags...`,
        `[0.55s] Sample 1..5: PASS (Score: 1.00) | Sample 6..10: PASS (Score: 0.96)`,
      ]);
    }, 850);

    setTimeout(() => {
      setSimLogs((prev) => [
        ...prev,
        `[0.68s] Generating chain-of-thought verification traces & score distribution... DONE`,
        `[0.82s] Evaluation run completed in 820ms. Overall pass rate: 100% | Status: GATE_PASSED`,
      ]);
      setSimRunning(false);
      setSimCompleted(true);
    }, 1150);
  };

  const handleCopyTerminalCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setTerminalCodeCopied(true);
    setTimeout(() => setTerminalCodeCopied(false), 2000);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSelectedCap(null);
        setSelectedTech(null);
        setPlatformModalOpen(false);
        setActiveDocModal(null);
      }
    };
    if (selectedCap || selectedTech || platformModalOpen || activeDocModal) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [selectedCap, selectedTech, platformModalOpen, activeDocModal]);

  useEffect(() => {
    const handleHash = () => {
      if (window.location.hash === '#platform') {
        const el = document.getElementById('platform');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }
    };
    handleHash();
    window.addEventListener('hashchange', handleHash);
    return () => window.removeEventListener('hashchange', handleHash);
  }, []);

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  const handleCopyTechCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedTechCode(true);
    setTimeout(() => setCopiedTechCode(false), 2000);
  };

  return (
    <div className="editorial-landing min-h-screen bg-[var(--bg)] text-[var(--text)] selection:bg-[#B0C2C6]/30 transition-colors duration-200">
      {/* ─── Top Editorial Notification / Status Bar ─── */}
      <div className="border-b border-[var(--border)] bg-[var(--surface)]/80 px-4 py-2 text-xs text-[var(--muted)]">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-[#0284C7] animate-pulse" />
            <span className="font-mono font-medium">EvalForge v1.0.0 Released</span>
            <span className="hidden sm:inline text-[#7E939C]">|</span>
            <span className="hidden sm:inline">Production-grade LLM evaluation infrastructure</span>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="https://github.com/hardikkaurani/Eval-Forge"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-[#0284C7] transition-colors flex items-center gap-1 font-mono"
            >
              <Github size={13} />
              <span>GitHub</span>
              <ExternalLink size={11} />
            </a>
            <ThemeControl />
          </div>
        </div>
      </div>

      {/* ─── Main Minimal Header ─── */}
      <header className="sticky top-0 z-40 backdrop-blur-md bg-[var(--bg)]/90 border-b border-[var(--border)]">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          {/* Brand Monogram & Wordmark */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative w-10 h-10 flex items-center justify-center transition-transform duration-200 group-hover:scale-105">
              <img
                src="/logo.png"
                alt="EvalForge Emblem"
                className="w-10 h-10 object-contain drop-shadow-sm"
              />
            </div>
            <div className="flex flex-col">
              <span className="font-sans text-2xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE] leading-none">
                EvalForge
              </span>
              <span className="text-[10px] font-mono tracking-widest uppercase text-[#7E939C] mt-1">
                AI Infrastructure
              </span>
            </div>
          </Link>

          {/* Desktop Minimal Nav */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-[#4C5F6B] dark:text-[#B0C2C6]">
            <button
              type="button"
              onClick={() => {
                setPlatformModalOpen(true);
                const el = document.getElementById('platform');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }}
              className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors cursor-pointer font-medium text-sm text-[#4C5F6B] dark:text-[#B0C2C6]"
              aria-label="Open Platform Overview"
            >
              <span>Platform</span>
            </button>
            <a
              href="#capabilities"
              className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
            >
              Capabilities
            </a>
            <a
              href="#workflow"
              className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
            >
              Workflow
            </a>
            <a
              href="#code"
              className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
            >
              Developer SDK
            </a>
            <a
              href="#benchmarks"
              className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors flex items-center gap-1.5"
            >
              <span>Benchmarks</span>
              <span className="px-1.5 py-0.5 rounded-full text-[10px] font-mono bg-[#0284C7]/15 text-[#0284C7] dark:text-[#38BDF8]">
                Matrix
              </span>
            </a>
            <a
              href="#architecture"
              className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
            >
              Architecture
            </a>
          </nav>

          {/* Primary Action CTA */}
          <div className="hidden md:flex items-center gap-4">
            {connected ? (
              <Link
                to="/overview"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-[#2E3A44] hover:bg-[#1C252C] dark:bg-[#F6F4EE] dark:hover:bg-[#EFECE4] text-[#F6F4EE] dark:text-[#2E3A44] text-xs font-semibold uppercase tracking-wider transition-all duration-200 shadow-sm"
              >
                <span>Enter Workspace</span>
                <ArrowRight size={14} />
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-xs font-semibold uppercase tracking-wider text-[#4C5F6B] hover:text-[#0284C7] dark:text-[#B0C2C6] dark:hover:text-[#38BDF8] transition-colors px-3 py-2"
                >
                  Sign In
                </Link>
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold uppercase tracking-wider transition-all duration-200 shadow-sm hover:shadow"
                >
                  <span>Connect Workspace</span>
                  <ArrowRight size={14} />
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-2">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-[#4C5F6B] dark:text-[#B0C2C6] border border-[#DDE4E1] dark:border-[#2E3A44] rounded-md"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden px-6 py-6 border-b border-[#DDE4E1] dark:border-[#2E3A44] bg-[#F6F4EE] dark:bg-[#182026] space-y-4">
            <button
              type="button"
              onClick={() => {
                setMobileMenuOpen(false);
                setPlatformModalOpen(true);
                const el = document.getElementById('platform');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }}
              className="w-full text-left text-base font-medium text-[#4C5F6B] dark:text-[#B0C2C6] hover:text-[#0284C7] dark:hover:text-[#38BDF8]"
            >
              <span>Platform Overview</span>
            </button>
            <a
              href="#capabilities"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-base font-medium text-[#4C5F6B] dark:text-[#B0C2C6]"
            >
              Capabilities
            </a>
            <a
              href="#workflow"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-base font-medium text-[#4C5F6B] dark:text-[#B0C2C6]"
            >
              Workflow
            </a>
            <a
              href="#code"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-base font-medium text-[#4C5F6B] dark:text-[#B0C2C6]"
            >
              Developer SDK
            </a>
            <a
              href="#benchmarks"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-base font-medium text-[#4C5F6B] dark:text-[#B0C2C6]"
            >
              Benchmarks Matrix
            </a>
            <a
              href="#architecture"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-base font-medium text-[#4C5F6B] dark:text-[#B0C2C6]"
            >
              Architecture
            </a>
            <div className="pt-4 border-t border-[#DDE4E1] dark:border-[#2E3A44] flex flex-col gap-3">
              <Link
                to={connected ? '/overview' : '/login'}
                className="w-full text-center py-3 rounded-full bg-[#0284C7] text-white text-sm font-semibold uppercase tracking-wider"
              >
                {connected ? 'Enter Workspace' : 'Connect Workspace'}
              </Link>
            </div>
          </div>
        )}
      </header>

      {/* ─── Hero Section: Alpaca Editorial Composition ─── */}
      <section
        id="platform"
        className="relative overflow-hidden pt-12 pb-24 border-b border-[#DDE4E1] dark:border-[#2E3A44]"
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            {/* Left Column: Editorial Typography & Value */}
            <div className="lg:col-span-7 space-y-8">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#B0C2C6] dark:border-[#4C5F6B] text-[11px] font-mono tracking-wider uppercase text-[#7E939C] dark:text-[#B0C2C6] bg-white/50 dark:bg-black/20">
                <ShieldCheck size={13} className="text-[#0284C7]" />
                <span>Deterministic AI Quality & Benchmark Suite</span>
              </div>

              <h1 className="font-sans text-5xl sm:text-6xl lg:text-7xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE] leading-[1.08]">
                Evaluate AI <br />
                <span className="text-[#0369A1] dark:text-[#38BDF8]">with unyielding rigor.</span>
              </h1>

              <p className="text-lg sm:text-xl text-[#4C5F6B] dark:text-[#B0C2C6] font-normal leading-relaxed max-w-2xl">
                Production-grade infrastructure for evaluating LLMs, RAG pipelines, and agentic
                systems. Benchmark reasoning, measure grounding, and enforce safety across
                reproducible datasets.
              </p>

              <div className="pt-2 flex flex-wrap items-center gap-4">
                <Link
                  to={connected ? '/overview' : '/login'}
                  className="inline-flex items-center gap-3 px-8 py-4 rounded-full bg-[#2E3A44] hover:bg-[#1C252C] dark:bg-[#F6F4EE] dark:hover:bg-[#EFECE4] text-[#F6F4EE] dark:text-[#2E3A44] text-sm font-semibold uppercase tracking-wider transition-all duration-200 shadow-md group"
                >
                  <span>{connected ? 'Open Workspace' : 'Get Started with Workspace'}</span>
                  <ArrowRight
                    size={16}
                    className="transition-transform group-hover:translate-x-1"
                  />
                </Link>

                <a
                  href="https://github.com/hardikkaurani/Eval-Forge"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-7 py-4 rounded-full border border-[#B0C2C6] dark:border-[#4C5F6B] hover:border-[#2E3A44] dark:hover:border-[#F6F4EE] text-sm font-medium text-[#2E3A44] dark:text-[#F6F4EE] bg-transparent transition-all duration-200"
                >
                  <Github size={17} />
                  <span>Star on GitHub</span>
                  <ArrowUpRight size={14} className="text-[#7E939C]" />
                </a>
              </div>

              {/* Technical Credibility Strip */}
              <div className="pt-6 border-t border-[#DDE4E1] dark:border-[#2E3A44] grid grid-cols-3 gap-6 font-mono text-xs text-[#7E939C] dark:text-[#B0C2C6]">
                <div>
                  <div className="text-xl sm:text-2xl font-sans font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                    180+
                  </div>
                  <div className="text-[11px] uppercase tracking-wider mt-0.5">Automated Tests</div>
                </div>
                <div>
                  <div className="text-xl sm:text-2xl font-sans font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                    114
                  </div>
                  <div className="text-[11px] uppercase tracking-wider mt-0.5">REST Endpoints</div>
                </div>
                <div>
                  <div className="text-xl sm:text-2xl font-sans font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                    v1.0.0
                  </div>
                  <div className="text-[11px] uppercase tracking-wider mt-0.5">
                    Production Ready
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Live Product Card Showcase */}
            <div className="lg:col-span-5 relative">
              <div
                onClick={() => setPlatformModalOpen(true)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    setPlatformModalOpen(true);
                  }
                }}
                className="relative rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#202A32] p-6 shadow-xl space-y-6 cursor-pointer hover:border-[#0284C7] dark:hover:border-[#38BDF8] transition-all hover:shadow-2xl group"
              >
                {/* Header of Preview Box */}
                <div className="flex items-center justify-between border-b border-[#DDE4E1] dark:border-[#2E3A44] pb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 flex items-center justify-center">
                      <img
                        src="/logo.png"
                        alt="EvalForge"
                        className="w-8 h-8 object-contain drop-shadow-sm"
                      />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-[#2E3A44] dark:text-[#F6F4EE] group-hover:text-[#0284C7] dark:group-hover:text-[#38BDF8] transition-colors">
                        Live Evaluation Dashboard
                      </div>
                      <div className="text-[10px] font-mono text-[#7E939C]">
                        Project: Chatbot Alignment · Click to Inspect Platform
                      </div>
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-[11px] font-mono font-medium flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Completed
                  </span>
                </div>

                {/* Score Summary Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#F6F4EE] dark:bg-[#182026]">
                    <div className="text-[11px] font-mono uppercase text-[#7E939C]">Pass Rate</div>
                    <div className="text-3xl font-sans font-semibold text-[#0369A1] dark:text-[#38BDF8] mt-1">
                      94.2%
                    </div>
                    <div className="text-[10px] text-[#4C5F6B] dark:text-[#B0C2C6] mt-1">
                      48 of 51 test criteria passed
                    </div>
                  </div>
                  <div className="p-4 rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#F6F4EE] dark:bg-[#182026]">
                    <div className="text-[11px] font-mono uppercase text-[#7E939C]">
                      Mean Latency
                    </div>
                    <div className="text-3xl font-sans font-semibold text-[#2E3A44] dark:text-[#F6F4EE] mt-1">
                      342ms
                    </div>
                    <div className="text-[10px] text-[#4C5F6B] dark:text-[#B0C2C6] mt-1">
                      p95 @ 610ms across runs
                    </div>
                  </div>
                </div>

                {/* Live Model Comparison Row */}
                <div className="space-y-3">
                  <div className="text-xs font-mono uppercase tracking-wider text-[#7E939C]">
                    Recent Judge Evaluations
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-3 rounded-lg border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#1C252C] text-xs">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 size={15} className="text-emerald-500" />
                        <span className="font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                          Claude 3.5 Sonnet Alignment
                        </span>
                      </div>
                      <span className="font-mono text-[#7E939C]">G-Eval Score: 4.85 / 5.0</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#1C252C] text-xs">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 size={15} className="text-emerald-500" />
                        <span className="font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                          GPT-4o RAG Grounding
                        </span>
                      </div>
                      <span className="font-mono text-[#7E939C]">Precision: 92.4%</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#1C252C] text-xs">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 size={15} className="text-emerald-500" />
                        <span className="font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                          Safety & Toxicity Filter v2
                        </span>
                      </div>
                      <span className="font-mono text-[#7E939C]">0 Violations</span>
                    </div>
                  </div>
                </div>

                {/* Quick Link into Overview */}
                <Link
                  to={connected ? '/overview' : '/login'}
                  className="block text-center text-xs font-medium text-[#0284C7] dark:text-[#38BDF8] hover:underline pt-1"
                >
                  Inspect complete evaluation results in workspace →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Editorial Problem & Philosophy Statement ─── */}
      <section className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
        <div className="max-w-5xl mx-auto px-6 text-center space-y-8">
          <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C]">
            The Engineering Dilemma
          </div>
          <h2 className="font-sans text-3xl sm:text-5xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE] leading-snug">
            “AI systems look impressive in isolation. <br />
            <span>Production systems demand empirical evidence.”</span>
          </h2>
          <div className="w-16 h-[1px] bg-[#0284C7] mx-auto" />
          <p className="text-base sm:text-lg text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed max-w-3xl mx-auto font-normal">
            Without structured benchmarks and automated evaluation pipelines, teams deploy updates
            into the dark. EvalForge introduces continuous statistical verification across reasoning
            quality, retrieval faithfulness, hallucination detection, and safety policies.
          </p>
        </div>
      </section>

      {/* ─── Numbered Editorial Capabilities (01 - 06) ─── */}
      <section id="capabilities" className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="mb-16 flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-[#0284C7]/10 text-[#0284C7] dark:text-[#38BDF8] dark:bg-[#0284C7]/20 border border-[#0284C7]/20 mb-3">
                <Sparkles size={12} />
                <span>Interactive Pillars — Click any card to inspect architecture & specs</span>
              </div>
              <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C] mb-2">
                01 — 06 Pillars
              </div>
              <h2 className="font-sans text-4xl sm:text-5xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE]">
                Architected for precision.
              </h2>
            </div>
            <p className="text-sm text-[#4C5F6B] dark:text-[#B0C2C6] max-w-md">
              Every capability is built as a first-class citizen of the evaluation lifecycle. Click
              any pillar to explore technical specifications and integration code.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {CAPABILITIES.map((cap) => (
              <div
                key={cap.num}
                role="button"
                tabIndex={0}
                aria-haspopup="dialog"
                aria-expanded={selectedCap?.num === cap.num}
                onClick={() => {
                  setSelectedCap(cap);
                  setModalTab('specs');
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    setSelectedCap(cap);
                    setModalTab('specs');
                  }
                }}
                className="group relative p-8 rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#202A32] hover:border-[#0284C7] dark:hover:border-[#38BDF8] hover:shadow-xl hover:-translate-y-1.5 transition-all duration-200 cursor-pointer flex flex-col justify-between text-left focus:outline-none focus:ring-2 focus:ring-[#0284C7] focus:ring-offset-2 dark:focus:ring-offset-[#1C252C]"
              >
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <span className="font-sans text-3xl font-semibold text-[#7E939C] group-hover:text-[#0284C7] dark:group-hover:text-[#38BDF8] transition-colors">
                      {cap.num}
                    </span>
                    <div className="p-2.5 rounded-lg border border-[#DDE4E1] dark:border-[#2E3A44] text-[#4C5F6B] dark:text-[#B0C2C6] group-hover:border-[#0284C7] group-hover:text-[#0284C7] dark:group-hover:border-[#38BDF8] dark:group-hover:text-[#38BDF8] transition-colors">
                      <cap.icon size={18} />
                    </div>
                  </div>
                  <h3 className="font-sans text-2xl font-semibold text-[#2E3A44] dark:text-[#F6F4EE] mb-3 group-hover:text-[#0284C7] dark:group-hover:text-[#38BDF8] transition-colors">
                    {cap.title}
                  </h3>
                  <p className="text-sm text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed">
                    {cap.desc}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-[#DDE4E1]/80 dark:border-[#2E3A44]/80 flex items-center justify-between text-xs font-medium text-[#0284C7] dark:text-[#38BDF8]">
                  <span className="flex items-center gap-1.5 group-hover:underline">
                    <span>Explore technical specs</span>
                    <ArrowRight
                      size={14}
                      className="transform group-hover:translate-x-1 transition-transform"
                    />
                  </span>
                  <span className="font-mono text-[11px] text-[#7E939C] uppercase tracking-wider">
                    Inspect
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* ─── Capability Detail Modal Dialog ─── */}
          {selectedCap && (
            <div
              role="dialog"
              aria-modal="true"
              aria-labelledby="capability-modal-title"
              className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-sm animate-fade-in"
              onClick={() => setSelectedCap(null)}
            >
              <div
                className="relative w-full max-w-2xl bg-white dark:bg-[#202A32] rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] shadow-2xl p-6 sm:p-8 overflow-hidden max-h-[90vh] flex flex-col text-left text-[var(--text)]"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Modal Header */}
                <div className="flex items-start justify-between pb-5 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-[#0284C7] to-[#0369A1] text-white shadow-sm flex items-center justify-center shrink-0">
                      <selectedCap.icon size={22} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-xs font-semibold tracking-wider text-[#0284C7] dark:text-[#38BDF8] uppercase">
                          Pillar {selectedCap.num} / Capability Architecture
                        </span>
                      </div>
                      <h3
                        id="capability-modal-title"
                        className="text-2xl sm:text-3xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE]"
                      >
                        {selectedCap.title}
                      </h3>
                      <p className="text-xs sm:text-sm text-[#4C5F6B] dark:text-[#B0C2C6] mt-1">
                        {selectedCap.tagline}
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedCap(null)}
                    className="p-2 rounded-lg text-[#7E939C] hover:text-[#2E3A44] dark:hover:text-[#F6F4EE] hover:bg-black/5 dark:hover:bg-white/5 transition-colors focus:outline-none focus:ring-2 focus:ring-[#0284C7]"
                    aria-label="Close capability details"
                  >
                    <X size={20} />
                  </button>
                </div>

                {/* Sub Navigation Tabs */}
                <div className="flex items-center gap-2 pt-4 pb-2 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
                  <button
                    type="button"
                    onClick={() => setModalTab('specs')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                      modalTab === 'specs'
                        ? 'bg-[#0284C7] text-white shadow-sm'
                        : 'text-[#4C5F6B] dark:text-[#B0C2C6] hover:bg-black/5 dark:hover:bg-white/5'
                    }`}
                  >
                    Architecture & Specs
                  </button>
                  <button
                    type="button"
                    onClick={() => setModalTab('code')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                      modalTab === 'code'
                        ? 'bg-[#0284C7] text-white shadow-sm'
                        : 'text-[#4C5F6B] dark:text-[#B0C2C6] hover:bg-black/5 dark:hover:bg-white/5'
                    }`}
                  >
                    Integration Code ({selectedCap.codeLanguage})
                  </button>
                </div>

                {/* Modal Body */}
                <div className="overflow-y-auto flex-1 py-5 space-y-6">
                  {modalTab === 'specs' ? (
                    <>
                      <div>
                        <h4 className="text-xs font-mono uppercase tracking-wider text-[#7E939C] mb-3">
                          Key Platform Capabilities
                        </h4>
                        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                          {selectedCap.highlights.map((highlight, idx) => (
                            <li
                              key={idx}
                              className="flex items-start gap-2 text-xs sm:text-sm text-[#2E3A44] dark:text-[#E2E8F0] p-2.5 rounded-lg bg-[#EFECE4]/40 dark:bg-[#1C252C]/60 border border-[#DDE4E1] dark:border-[#2E3A44]"
                            >
                              <CheckCircle2 size={16} className="text-[#0284C7] shrink-0 mt-0.5" />
                              <span>{highlight}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <h4 className="text-xs font-mono uppercase tracking-wider text-[#7E939C] mb-3">
                          Technical Specifications
                        </h4>
                        <div className="rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] overflow-hidden divide-y divide-[#DDE4E1] dark:divide-[#2E3A44] text-xs">
                          {selectedCap.specs.map((spec, idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between p-3 bg-white dark:bg-[#202A32]"
                            >
                              <span className="font-mono text-[#7E939C]">{spec.label}</span>
                              <span className="font-medium text-[#2E3A44] dark:text-[#F6F4EE] text-right">
                                {spec.value}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  ) : (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-mono uppercase tracking-wider text-[#7E939C]">
                          Snippet ({selectedCap.codeLanguage})
                        </span>
                        <button
                          type="button"
                          onClick={() => handleCopyCode(selectedCap.codeSnippet)}
                          className="flex items-center gap-1.5 text-xs font-mono px-2.5 py-1 rounded border border-[#DDE4E1] dark:border-[#2E3A44] hover:bg-black/5 dark:hover:bg-white/5 transition-colors text-[#0284C7] dark:text-[#38BDF8]"
                        >
                          {copiedCode ? <Check size={12} /> : <Copy size={12} />}
                          <span>{copiedCode ? 'Copied' : 'Copy snippet'}</span>
                        </button>
                      </div>
                      <pre className="p-4 rounded-xl bg-[#1C252C] dark:bg-[#0F172A] border border-[#2E3A44] dark:border-[#334155] text-xs text-[#E2E8F0] font-mono overflow-x-auto leading-relaxed">
                        <code>{selectedCap.codeSnippet}</code>
                      </pre>
                    </div>
                  )}
                </div>

                {/* Modal Footer */}
                <div className="pt-4 border-t border-[#DDE4E1] dark:border-[#2E3A44] flex flex-col sm:flex-row items-center justify-between gap-3">
                  <span className="text-xs text-[#7E939C]">
                    Pillar {selectedCap.num} is fully supported in SDK & API.
                  </span>
                  <div className="flex items-center gap-2.5 w-full sm:w-auto">
                    <button
                      type="button"
                      onClick={() => setSelectedCap(null)}
                      className="w-full sm:w-auto px-4 py-2 rounded-xl text-xs font-medium border border-[#DDE4E1] dark:border-[#2E3A44] text-[#4C5F6B] dark:text-[#B0C2C6] hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
                    >
                      Close
                    </button>
                    <Link
                      to={connected ? selectedCap.actionRoute : '/login'}
                      onClick={() => setSelectedCap(null)}
                      className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2 rounded-xl text-xs font-medium bg-[#0284C7] hover:bg-[#0369A1] text-white shadow-sm transition-colors"
                    >
                      <span>
                        {connected ? selectedCap.actionLabel : 'Connect Workspace to Access'}
                      </span>
                      <ArrowRight size={13} />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ─── Workflow Section: Connected Journey ─── */}
      <section
        id="workflow"
        className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44] bg-[#EFECE4]/50 dark:bg-[#1C252C]/40"
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C]">
              Execution Pipeline
            </div>
            <h2 className="font-sans text-4xl sm:text-5xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE]">
              The Evaluation Lifecycle
            </h2>
            <p className="text-sm text-[#4C5F6B] dark:text-[#B0C2C6]">
              From dataset ingestion to production release gating in a single unified protocol.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative">
            {[
              { step: '01', title: 'Dataset', desc: 'Versioned golden questions and contexts' },
              { step: '02', title: 'Evaluation', desc: 'G-Eval rubrics and LLM judge models' },
              { step: '03', title: 'Async Job', desc: 'Distributed queue execution on Celery' },
              { step: '04', title: 'Verdict', desc: 'Score distributions and reasoning logs' },
              { step: '05', title: 'Decision', desc: 'Automated CI/CD pass/fail gates' },
            ].map((st) => (
              <div
                key={st.step}
                className="p-6 rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#202A32] flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="font-mono text-xs text-[#0284C7] dark:text-[#38BDF8] font-bold">
                    STEP {st.step}
                  </div>
                  <h4 className="font-sans text-xl font-semibold text-[#2E3A44] dark:text-[#F6F4EE] mt-2">
                    {st.title}
                  </h4>
                </div>
                <p className="text-xs text-[#4C5F6B] dark:text-[#B0C2C6] leading-normal">
                  {st.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Developer SDK & Code Showcase ─── */}
      <section id="code" className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-5 space-y-6">
              <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C]">
                First-Party Tooling
              </div>
              <h2 className="font-sans text-4xl sm:text-5xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE]">
                Designed for engineers, <br />
                <span className="text-[#0369A1] dark:text-[#38BDF8]">native to your stack.</span>
              </h2>
              <p className="text-sm sm:text-base text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed">
                Integrate evaluation steps directly into your unit tests, regression pipelines, or
                agent loops. Use our lightweight Python SDK, TypeScript client, or CLI to trigger
                runs in one line.
              </p>

              <div className="space-y-3 pt-2">
                <div className="flex items-center gap-3 text-xs font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                  <CheckCircle2 size={16} className="text-[#0284C7]" />
                  <span>Python SDK with async client support</span>
                </div>
                <div className="flex items-center gap-3 text-xs font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                  <CheckCircle2 size={16} className="text-[#0284C7]" />
                  <span>TypeScript / JavaScript SDK for Next.js & Node</span>
                </div>
                <div className="flex items-center gap-3 text-xs font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                  <CheckCircle2 size={16} className="text-[#0284C7]" />
                  <span>Standalone terminal CLI (`evalforge run ...`)</span>
                </div>
              </div>
            </div>

            <div className="lg:col-span-7">
              <div className="rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#2E3A44] text-[#F6F4EE] overflow-hidden shadow-xl">
                {/* Code Tabs */}
                <div className="flex items-center justify-between border-b border-[#4C5F6B]/40 px-4 py-3 bg-[#232E37]">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500/80" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                    <div className="w-3 h-3 rounded-full bg-green-500/80" />
                  </div>
                  <div className="flex items-center gap-2">
                    {(['python', 'cli', 'rest'] as const).map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveCodeTab(tab)}
                        className={`px-3 py-1 rounded text-xs font-mono uppercase tracking-wider transition-colors ${
                          activeCodeTab === tab
                            ? 'bg-[#0284C7] text-white shadow-sm'
                            : 'text-[#B0C2C6] hover:text-white'
                        }`}
                      >
                        {tab}
                      </button>
                    ))}
                    <button
                      onClick={() => {
                        setActiveCodeTab('simulator');
                        if (!simCompleted && !simRunning) runSimulation();
                      }}
                      className={`px-3 py-1 rounded text-xs font-mono uppercase tracking-wider transition-colors flex items-center gap-1.5 ${
                        activeCodeTab === 'simulator'
                          ? 'bg-emerald-600 text-white shadow-sm'
                          : 'text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 border border-emerald-500/30'
                      }`}
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      <span>Simulator ▶</span>
                    </button>
                  </div>

                  {activeCodeTab !== 'simulator' && (
                    <button
                      onClick={() => {
                        const snippets: Record<string, string> = {
                          python: `from evalforge import EvalForgeClient\nclient = EvalForgeClient(api_key="ef_live_...")\njob = client.evaluations.create(project_id="proj_chatbot_v1", dataset_id="ds_qa_golden", metrics=["g_eval_faithfulness", "context_precision"], judge_model="gpt-4o")\nresults = job.wait_for_completion()\nprint(f"Pass rate: {results.pass_rate}%")`,
                          cli: `$ pip install evalforge-cli\n$ evalforge login --api-key ef_live_...\n$ evalforge run --project "proj_chatbot_v1" --dataset "./tests/benchmarks.jsonl" --metric g-eval --threshold 0.85`,
                          rest: `curl -X POST https://evalforge-backend.onrender.com/api/v1/evaluations/run -H "Authorization: Bearer ef_live_..." -H "Content-Type: application/json" -d '{"project_id":"proj_chatbot_v1","dataset_id":"ds_qa_golden","judge_model":"claude-3-5-sonnet"}'`,
                        };
                        handleCopyTerminalCode(snippets[activeCodeTab] || '');
                      }}
                      className="hidden sm:flex items-center gap-1.5 text-xs font-mono px-2.5 py-1 rounded border border-[#4C5F6B] hover:bg-white/5 transition-colors text-[#B0C2C6] hover:text-white"
                      title="Copy snippet"
                    >
                      {terminalCodeCopied ? (
                        <Check size={12} className="text-emerald-400" />
                      ) : (
                        <Copy size={12} />
                      )}
                      <span>{terminalCodeCopied ? 'Copied' : 'Copy'}</span>
                    </button>
                  )}
                </div>

                {/* Code Block / Simulator View */}
                <div className="p-6 font-mono text-xs sm:text-sm leading-relaxed overflow-x-auto">
                  {activeCodeTab === 'python' && (
                    <div className="space-y-4">
                      <pre className="text-[#DDE4E1]">
                        <span className="text-[#7E939C]"># pip install evalforge-sdk</span>
                        <br />
                        <span className="text-[#38BDF8]">from</span> evalforge{' '}
                        <span className="text-[#38BDF8]">import</span> EvalForgeClient
                        <br />
                        <br />
                        client = EvalForgeClient(api_key=
                        <span className="text-emerald-400">&quot;ef_live_...&quot;</span>)
                        <br />
                        <br />
                        <span className="text-[#7E939C]"># Trigger asynchronous G-Eval run</span>
                        <br />
                        job = client.evaluations.create(
                        <br />
                        &nbsp;&nbsp;project_id=
                        <span className="text-emerald-400">&quot;proj_chatbot_v1&quot;</span>,<br />
                        &nbsp;&nbsp;dataset_id=
                        <span className="text-emerald-400">&quot;ds_qa_golden&quot;</span>,<br />
                        &nbsp;&nbsp;metrics=[
                        <span className="text-emerald-400">
                          &quot;g_eval_faithfulness&quot;
                        </span>,{' '}
                        <span className="text-emerald-400">&quot;context_precision&quot;</span>],
                        <br />
                        &nbsp;&nbsp;judge_model=
                        <span className="text-emerald-400">&quot;gpt-4o&quot;</span>
                        <br />
                        )
                        <br />
                        <br />
                        results = job.wait_for_completion()
                        <br />
                        <span className="text-[#38BDF8]">print</span>(f
                        <span className="text-emerald-400">
                          &quot;Pass rate: &#123;results.pass_rate&#125;%&quot;
                        </span>
                        )
                      </pre>
                      <div className="pt-3 border-t border-[#4C5F6B]/40 flex items-center justify-between text-xs">
                        <span className="text-[#7E939C]">Ready to test this snippet live?</span>
                        <button
                          type="button"
                          onClick={() => runSimulation()}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold uppercase tracking-wider transition-colors shadow-sm"
                        >
                          <Play size={12} />
                          <span>Simulate Run</span>
                        </button>
                      </div>
                    </div>
                  )}

                  {activeCodeTab === 'cli' && (
                    <div className="space-y-4">
                      <pre className="text-[#DDE4E1]">
                        <span className="text-[#7E939C]"># Install EvalForge CLI</span>
                        <br />
                        $ pip install evalforge-cli
                        <br />
                        <br />
                        <span className="text-[#7E939C]"># Authenticate workspace</span>
                        <br />
                        $ evalforge login --api-key ef_live_...
                        <br />
                        <br />
                        <span className="text-[#7E939C]"># Run evaluation against dataset</span>
                        <br />
                        $ evalforge run \
                        <br />
                        &nbsp;&nbsp;--project &quot;proj_chatbot_v1&quot; \
                        <br />
                        &nbsp;&nbsp;--dataset &quot;./tests/benchmarks.jsonl&quot; \
                        <br />
                        &nbsp;&nbsp;--metric g-eval \
                        <br />
                        &nbsp;&nbsp;--threshold 0.85
                      </pre>
                      <div className="pt-3 border-t border-[#4C5F6B]/40 flex items-center justify-between text-xs">
                        <span className="text-[#7E939C]">Test CLI terminal execution:</span>
                        <button
                          type="button"
                          onClick={() => runSimulation('rubric')}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold uppercase tracking-wider transition-colors shadow-sm"
                        >
                          <Play size={12} />
                          <span>Simulate Run</span>
                        </button>
                      </div>
                    </div>
                  )}

                  {activeCodeTab === 'rest' && (
                    <div className="space-y-4">
                      <pre className="text-[#DDE4E1]">
                        curl -X POST https://evalforge-backend.onrender.com/api/v1/evaluations/run \
                        <br />
                        &nbsp;&nbsp;-H{' '}
                        <span className="text-emerald-400">
                          &quot;Authorization: Bearer ef_live_...&quot;
                        </span>{' '}
                        \
                        <br />
                        &nbsp;&nbsp;-H{' '}
                        <span className="text-emerald-400">
                          &quot;Content-Type: application/json&quot;
                        </span>{' '}
                        \
                        <br />
                        &nbsp;&nbsp;-d &apos;&#123;
                        <br />
                        &nbsp;&nbsp;&nbsp;&nbsp;
                        <span className="text-[#38BDF8]">&quot;project_id&quot;</span>:{' '}
                        <span className="text-emerald-400">&quot;proj_chatbot_v1&quot;</span>,
                        <br />
                        &nbsp;&nbsp;&nbsp;&nbsp;
                        <span className="text-[#38BDF8]">&quot;dataset_id&quot;</span>:{' '}
                        <span className="text-emerald-400">&quot;ds_qa_golden&quot;</span>,
                        <br />
                        &nbsp;&nbsp;&nbsp;&nbsp;
                        <span className="text-[#38BDF8]">&quot;judge_model&quot;</span>:{' '}
                        <span className="text-emerald-400">&quot;claude-3-5-sonnet&quot;</span>
                        <br />
                        &nbsp;&nbsp;&#125;&apos;
                      </pre>
                      <div className="pt-3 border-t border-[#4C5F6B]/40 flex items-center justify-between text-xs">
                        <span className="text-[#7E939C]">Trigger evaluation over REST API:</span>
                        <button
                          type="button"
                          onClick={() => runSimulation('safety')}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold uppercase tracking-wider transition-colors shadow-sm"
                        >
                          <Play size={12} />
                          <span>Simulate Run</span>
                        </button>
                      </div>
                    </div>
                  )}

                  {activeCodeTab === 'simulator' && (
                    <div className="space-y-4">
                      {/* Suite Selector */}
                      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-[#232E37] border border-[#4C5F6B]/40">
                        <div className="flex items-center gap-1.5 text-xs font-mono">
                          <span className="text-[#7E939C] hidden sm:inline">Suite:</span>
                          {(['rag', 'rubric', 'safety'] as const).map((s) => (
                            <button
                              key={s}
                              type="button"
                              onClick={() => {
                                setSimSuite(s);
                                runSimulation(s);
                              }}
                              disabled={simRunning}
                              className={`px-2.5 py-1 rounded text-[11px] font-mono uppercase tracking-wider transition-colors ${
                                simSuite === s
                                  ? 'bg-[#0284C7] text-white'
                                  : 'text-[#B0C2C6] hover:text-white bg-black/20'
                              }`}
                            >
                              {s === 'rag'
                                ? 'RAG Triad'
                                : s === 'rubric'
                                  ? 'CoT Rubric'
                                  : 'Safety Gate'}
                            </button>
                          ))}
                        </div>

                        <button
                          type="button"
                          onClick={() => runSimulation()}
                          disabled={simRunning}
                          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-medium text-xs transition-colors"
                        >
                          {simRunning ? (
                            <RotateCcw size={12} className="animate-spin" />
                          ) : (
                            <Play size={12} />
                          )}
                          <span>{simRunning ? 'Evaluating...' : 'Run Suite'}</span>
                        </button>
                      </div>

                      {/* Log Console */}
                      <div className="p-4 rounded-xl bg-[#141D24] border border-[#334155] font-mono text-xs space-y-1.5 max-h-48 overflow-y-auto">
                        {simLogs.map((log, index) => (
                          <div key={index} className="flex items-start gap-2 leading-relaxed">
                            <span className="text-[#38BDF8] select-none">&gt;</span>
                            <span
                              className={
                                log.includes('PASSED') ||
                                log.includes('OK') ||
                                log.includes('CONNECTED') ||
                                log.includes('DONE')
                                  ? 'text-emerald-300'
                                  : 'text-[#DDE4E1]'
                              }
                            >
                              {log}
                            </span>
                          </div>
                        ))}
                        {simRunning && (
                          <div className="flex items-center gap-2 text-[#38BDF8] text-xs pt-1">
                            <span className="inline-block w-2 h-2 rounded-full bg-[#38BDF8] animate-ping" />
                            <span>Computing rubric distributions & regression slices...</span>
                          </div>
                        )}
                      </div>

                      {/* Live Score Verdict Card */}
                      {simCompleted && (
                        <div className="p-4 rounded-xl bg-[#232E37] border border-emerald-500/40 space-y-3 animate-fade-in">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <CheckCircle2 size={16} className="text-emerald-400" />
                              <span className="text-xs font-mono font-semibold text-emerald-300 uppercase tracking-wider">
                                Evaluation Verdict: PASSED (Threshold &ge; 0.85)
                              </span>
                            </div>
                            <span className="text-[10px] font-mono text-[#7E939C]">Lat: 184ms</span>
                          </div>

                          <div className="grid grid-cols-3 gap-2 text-center font-mono">
                            <div className="p-2 rounded-lg bg-[#182026] border border-[#4C5F6B]/30">
                              <div className="text-[10px] text-[#7E939C]">AGGREGATE SCORE</div>
                              <div className="text-base font-semibold text-emerald-400">
                                0.96 / 1.0
                              </div>
                            </div>
                            <div className="p-2 rounded-lg bg-[#182026] border border-[#4C5F6B]/30">
                              <div className="text-[10px] text-[#7E939C]">FAITHFULNESS</div>
                              <div className="text-base font-semibold text-[#38BDF8]">98.4%</div>
                            </div>
                            <div className="p-2 rounded-lg bg-[#182026] border border-[#4C5F6B]/30">
                              <div className="text-[10px] text-[#7E939C]">HALLUCINATIONS</div>
                              <div className="text-base font-semibold text-emerald-400">0 / 10</div>
                            </div>
                          </div>

                          <div className="pt-2 flex items-center justify-between text-xs">
                            <button
                              type="button"
                              onClick={() => runSimulation()}
                              className="text-[#B0C2C6] hover:text-white font-mono flex items-center gap-1"
                            >
                              <RotateCcw size={12} />
                              <span>Re-run test</span>
                            </button>
                            <Link
                              to={connected ? '/projects' : '/login'}
                              className="text-[#38BDF8] hover:underline font-mono flex items-center gap-1"
                            >
                              <span>Run against production datasets</span>
                              <ArrowRight size={12} />
                            </Link>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Sovereign Judge Matrix & Model Benchmarks ─── */}
      <section
        id="benchmarks"
        className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44] bg-[#EFECE4]/20 dark:bg-[#1C252C]/30"
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="mb-14 flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-[#0284C7]/10 text-[#0284C7] dark:text-[#38BDF8] dark:bg-[#0284C7]/20 border border-[#0284C7]/20 mb-3">
                <Gauge size={12} />
                <span>Frontier Evaluation Telemetry & Sovereign Benchmarks</span>
              </div>
              <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C] mb-2">
                Judge Performance Matrix
              </div>
              <h2 className="font-sans text-4xl sm:text-5xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE]">
                Sovereign Judge Matrix
              </h2>
            </div>
            <p className="text-sm text-[#4C5F6B] dark:text-[#B0C2C6] max-w-md">
              Benchmark factual precision, chain-of-thought latency, and token economics across
              foundation models deployed as automated evaluators.
            </p>
          </div>

          {/* Model Selector Tabs */}
          <div className="flex flex-wrap items-center gap-2 mb-8">
            {JUDGE_BENCHMARKS.map((model) => (
              <button
                key={model.id}
                type="button"
                onClick={() => setSelectedJudge(model.id)}
                className={`px-4 py-2 rounded-xl text-xs font-mono font-medium transition-all ${
                  selectedJudge === model.id
                    ? 'bg-[#0284C7] text-white shadow-md shadow-[#0284C7]/20 scale-105'
                    : 'bg-white dark:bg-[#202A32] text-[#4C5F6B] dark:text-[#B0C2C6] border border-[#DDE4E1] dark:border-[#2E3A44] hover:border-[#0284C7]'
                }`}
              >
                <span>{model.name}</span>
                <span className="ml-2 text-[10px] opacity-80 font-sans">({model.provider})</span>
              </button>
            ))}
          </div>

          {/* Active Model Dashboard */}
          {(() => {
            const currentModel =
              JUDGE_BENCHMARKS.find((m) => m.id === selectedJudge) ?? JUDGE_BENCHMARKS[0];
            return (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left: Metrics & Gauges */}
                <div className="lg:col-span-6 p-6 sm:p-8 rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#202A32] shadow-sm space-y-6">
                  <div className="flex items-center justify-between pb-4 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xl font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                          {currentModel.name}
                        </span>
                        <span className="text-xs font-mono text-[#7E939C]">
                          &middot; {currentModel.provider}
                        </span>
                      </div>
                      <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-[#0284C7]/10 text-[#0284C7] dark:text-[#38BDF8] border border-[#0284C7]/20">
                        {currentModel.badge}
                      </span>
                    </div>

                    <div className="text-right">
                      <div className="text-xs text-[#7E939C]">P95 Latency</div>
                      <div className="font-mono text-base font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                        {currentModel.latencyMs}ms
                      </div>
                    </div>
                  </div>

                  {/* Progress Bars */}
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-xs mb-1.5 font-mono">
                        <span className="text-[#4C5F6B] dark:text-[#B0C2C6]">
                          Factual Faithfulness
                        </span>
                        <span className="font-semibold text-[#0284C7] dark:text-[#38BDF8]">
                          {currentModel.faithfulness}%
                        </span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-[#EFECE4] dark:bg-[#1C252C] overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-[#0284C7] to-[#38BDF8] rounded-full transition-all duration-500"
                          style={{ width: `${currentModel.faithfulness}%` }}
                        />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1.5 font-mono">
                        <span className="text-[#4C5F6B] dark:text-[#B0C2C6]">
                          Chain-of-Thought Consistency
                        </span>
                        <span className="font-semibold text-[#0284C7] dark:text-[#38BDF8]">
                          {currentModel.cotReasoning}%
                        </span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-[#EFECE4] dark:bg-[#1C252C] overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-[#0284C7] to-[#38BDF8] rounded-full transition-all duration-500"
                          style={{ width: `${currentModel.cotReasoning}%` }}
                        />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1.5 font-mono">
                        <span className="text-[#4C5F6B] dark:text-[#B0C2C6]">
                          Hallucination Detection Precision
                        </span>
                        <span className="font-semibold text-[#0284C7] dark:text-[#38BDF8]">
                          {currentModel.hallucinationDetection}%
                        </span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-[#EFECE4] dark:bg-[#1C252C] overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-[#0284C7] to-[#38BDF8] rounded-full transition-all duration-500"
                          style={{ width: `${currentModel.hallucinationDetection}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Metadata Chips */}
                  <div className="grid grid-cols-2 gap-3 pt-3 border-t border-[#DDE4E1] dark:border-[#2E3A44] text-xs font-mono">
                    <div className="p-3 rounded-xl bg-[#EFECE4]/50 dark:bg-[#1C252C]/60 border border-[#DDE4E1] dark:border-[#2E3A44]">
                      <div className="text-[10px] text-[#7E939C] mb-1">EVAL COST (10K SAMPLES)</div>
                      <div className="font-semibold text-[#2E3A44] dark:text-[#F6F4EE] flex items-center gap-1">
                        <DollarSign size={13} className="text-[#0284C7]" />
                        <span>{currentModel.costPer10k}</span>
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-[#EFECE4]/50 dark:bg-[#1C252C]/60 border border-[#DDE4E1] dark:border-[#2E3A44]">
                      <div className="text-[10px] text-[#7E939C] mb-1">MAX CONTEXT WINDOW</div>
                      <div className="font-semibold text-[#2E3A44] dark:text-[#F6F4EE] flex items-center gap-1">
                        <Layers size={13} className="text-[#0284C7]" />
                        <span>{currentModel.contextWindow}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right: Chain-of-Thought Reasoning Sample */}
                <div className="lg:col-span-6 p-6 sm:p-8 rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#2E3A44] text-[#F6F4EE] shadow-sm flex flex-col justify-between space-y-6">
                  <div>
                    <div className="flex items-center justify-between pb-3 border-b border-[#4C5F6B]/40 mb-4">
                      <div className="flex items-center gap-2">
                        <Sliders size={14} className="text-[#38BDF8]" />
                        <span className="text-xs font-mono uppercase tracking-wider text-[#B0C2C6]">
                          Chain-of-Thought Verification Trace
                        </span>
                      </div>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono">
                        {currentModel.verdictSample.verdict}
                      </span>
                    </div>

                    <div className="space-y-3 font-mono text-xs">
                      <div>
                        <div className="text-[#7E939C] uppercase text-[10px] mb-1">
                          Question / Prompt:
                        </div>
                        <div className="p-3 rounded-lg bg-[#232E37] text-[#DDE4E1]">
                          &quot;{currentModel.verdictSample.question}&quot;
                        </div>
                      </div>

                      <div>
                        <div className="text-[#7E939C] uppercase text-[10px] mb-1">
                          Judge Chain-of-Thought Reasoning:
                        </div>
                        <div className="p-3 rounded-lg bg-[#232E37] text-emerald-300/90 leading-relaxed font-sans text-xs">
                          {currentModel.verdictSample.reasoning}
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-2">
                        <span className="text-[#7E939C]">Computed Rubric Score:</span>
                        <span className="font-semibold text-[#38BDF8] text-sm">
                          {currentModel.verdictSample.score}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-[#4C5F6B]/40 flex flex-col sm:flex-row items-center justify-between gap-3">
                    <span className="text-[11px] text-[#B0C2C6]">
                      Ready to calibrate with your custom evaluation dataset?
                    </span>
                    <Link
                      to={connected ? '/projects' : '/login'}
                      className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold uppercase tracking-wider transition-colors shadow-sm"
                    >
                      <span>Configure {currentModel.name}</span>
                      <ArrowRight size={13} />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      </section>

      {/* ─── Architecture & Open Source ─── */}
      <section
        id="architecture"
        className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44] bg-[#EFECE4]/30 dark:bg-[#1C252C]/20"
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-[#0284C7]/10 text-[#0284C7] dark:text-[#38BDF8] dark:bg-[#0284C7]/20 border border-[#0284C7]/20 mb-3">
              <Sparkles size={12} />
              <span>Interactive Topology — Click any technology to inspect specs & code</span>
            </div>
            <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C]">
              Infrastructure Topology
            </div>
            <h2 className="font-sans text-4xl sm:text-5xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE]">
              Full-Stack Architecture
            </h2>
            <p className="text-sm text-[#4C5F6B] dark:text-[#B0C2C6]">
              Modular, transparent, and battle-tested on standard production primitives. Click any
              primitive to explore configuration and architectural specs.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-center font-mono text-xs">
            {ARCHITECTURE_STACK.map((tech) => (
              <div
                key={tech.name}
                role="button"
                tabIndex={0}
                aria-haspopup="dialog"
                aria-expanded={selectedTech?.name === tech.name}
                onClick={() => {
                  setSelectedTech(tech);
                  setTechModalTab('specs');
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    setSelectedTech(tech);
                    setTechModalTab('specs');
                  }
                }}
                className="group relative p-5 rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#202A32] hover:border-[#0284C7] dark:hover:border-[#38BDF8] hover:shadow-lg hover:-translate-y-1 transition-all duration-200 cursor-pointer space-y-2 flex flex-col justify-between text-center focus:outline-none focus:ring-2 focus:ring-[#0284C7] focus:ring-offset-2 dark:focus:ring-offset-[#1C252C]"
              >
                <div className="space-y-1.5">
                  <div className="text-sm font-semibold text-[#2E3A44] dark:text-[#F6F4EE] group-hover:text-[#0284C7] dark:group-hover:text-[#38BDF8] transition-colors">
                    {tech.name}
                  </div>
                  <div className="text-[11px] text-[#4C5F6B] dark:text-[#B0C2C6] leading-tight">
                    {tech.role}
                  </div>
                  <span className="inline-block px-2 py-0.5 rounded bg-[#DDE4E1]/80 dark:bg-[#2E3A44] text-[10px] text-[#7E939C] dark:text-[#B0C2C6]">
                    {tech.badge}
                  </span>
                </div>

                <div className="pt-2 border-t border-[#DDE4E1]/60 dark:border-[#2E3A44]/60 text-[10px] text-[#0284C7] dark:text-[#38BDF8] flex items-center justify-center gap-1 group-hover:underline font-sans font-medium">
                  <span>Inspect</span>
                  <ArrowRight
                    size={11}
                    className="transform group-hover:translate-x-0.5 transition-transform"
                  />
                </div>
              </div>
            ))}
          </div>

          {/* ─── Technology Stack Detail Modal Dialog ─── */}
          {selectedTech && (
            <div
              role="dialog"
              aria-modal="true"
              aria-labelledby="tech-modal-title"
              className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-sm animate-fade-in"
              onClick={() => setSelectedTech(null)}
            >
              <div
                className="relative w-full max-w-2xl bg-white dark:bg-[#202A32] rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] shadow-2xl p-6 sm:p-8 overflow-hidden max-h-[90vh] flex flex-col text-left text-[var(--text)]"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Modal Header */}
                <div className="flex items-start justify-between pb-5 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-[#0284C7] to-[#0369A1] text-white shadow-sm flex items-center justify-center shrink-0">
                      <selectedTech.icon size={22} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-xs font-semibold tracking-wider text-[#0284C7] dark:text-[#38BDF8] uppercase">
                          Stack Primitive / {selectedTech.badge}
                        </span>
                      </div>
                      <h3
                        id="tech-modal-title"
                        className="text-2xl sm:text-3xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE]"
                      >
                        {selectedTech.name}
                      </h3>
                      <p className="text-xs sm:text-sm text-[#4C5F6B] dark:text-[#B0C2C6] mt-1">
                        {selectedTech.role} &middot; {selectedTech.overview}
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedTech(null)}
                    className="p-2 rounded-lg text-[#7E939C] hover:text-[#2E3A44] dark:hover:text-[#F6F4EE] hover:bg-black/5 dark:hover:bg-white/5 transition-colors focus:outline-none focus:ring-2 focus:ring-[#0284C7]"
                    aria-label="Close technology details"
                  >
                    <X size={20} />
                  </button>
                </div>

                {/* Sub Navigation Tabs */}
                <div className="flex items-center gap-2 pt-4 pb-2 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
                  <button
                    type="button"
                    onClick={() => setTechModalTab('specs')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                      techModalTab === 'specs'
                        ? 'bg-[#0284C7] text-white shadow-sm'
                        : 'text-[#4C5F6B] dark:text-[#B0C2C6] hover:bg-black/5 dark:hover:bg-white/5'
                    }`}
                  >
                    Architecture & Specs
                  </button>
                  <button
                    type="button"
                    onClick={() => setTechModalTab('code')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                      techModalTab === 'code'
                        ? 'bg-[#0284C7] text-white shadow-sm'
                        : 'text-[#4C5F6B] dark:text-[#B0C2C6] hover:bg-black/5 dark:hover:bg-white/5'
                    }`}
                  >
                    Configuration / Integration Code
                  </button>
                </div>

                {/* Modal Body */}
                <div className="overflow-y-auto flex-1 py-5 space-y-6">
                  {techModalTab === 'specs' ? (
                    <>
                      <div>
                        <h4 className="text-xs font-mono uppercase tracking-wider text-[#7E939C] mb-3">
                          Key Architectural Responsibilities
                        </h4>
                        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                          {selectedTech.highlights.map((highlight, idx) => (
                            <li
                              key={idx}
                              className="flex items-start gap-2 text-xs sm:text-sm text-[#2E3A44] dark:text-[#E2E8F0] p-2.5 rounded-lg bg-[#EFECE4]/40 dark:bg-[#1C252C]/60 border border-[#DDE4E1] dark:border-[#2E3A44]"
                            >
                              <CheckCircle2 size={16} className="text-[#0284C7] shrink-0 mt-0.5" />
                              <span>{highlight}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <h4 className="text-xs font-mono uppercase tracking-wider text-[#7E939C] mb-3">
                          Runtime Specifications
                        </h4>
                        <div className="rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] overflow-hidden divide-y divide-[#DDE4E1] dark:divide-[#2E3A44] text-xs">
                          {selectedTech.specs.map((spec, idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between p-3 bg-white dark:bg-[#202A32]"
                            >
                              <span className="font-mono text-[#7E939C]">{spec.label}</span>
                              <span className="font-medium text-[#2E3A44] dark:text-[#F6F4EE] text-right">
                                {spec.value}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  ) : (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-mono uppercase tracking-wider text-[#7E939C]">
                          Implementation Snippet ({selectedTech.codeLanguage})
                        </span>
                        <button
                          type="button"
                          onClick={() => handleCopyTechCode(selectedTech.codeSnippet)}
                          className="flex items-center gap-1.5 text-xs font-mono px-2.5 py-1 rounded border border-[#DDE4E1] dark:border-[#2E3A44] hover:bg-black/5 dark:hover:bg-white/5 transition-colors text-[#0284C7] dark:text-[#38BDF8]"
                        >
                          {copiedTechCode ? <Check size={12} /> : <Copy size={12} />}
                          <span>{copiedTechCode ? 'Copied' : 'Copy snippet'}</span>
                        </button>
                      </div>
                      <pre className="p-4 rounded-xl bg-[#1C252C] dark:bg-[#0F172A] border border-[#2E3A44] dark:border-[#334155] text-xs text-[#E2E8F0] font-mono overflow-x-auto leading-relaxed">
                        <code>{selectedTech.codeSnippet}</code>
                      </pre>
                    </div>
                  )}
                </div>

                {/* Modal Footer */}
                <div className="pt-4 border-t border-[#DDE4E1] dark:border-[#2E3A44] flex flex-col sm:flex-row items-center justify-between gap-3">
                  <span className="text-xs text-[#7E939C]">
                    {selectedTech.name} is configured for high-availability enterprise clusters.
                  </span>
                  <div className="flex items-center gap-2.5 w-full sm:w-auto">
                    <button
                      type="button"
                      onClick={() => setSelectedTech(null)}
                      className="w-full sm:w-auto px-4 py-2 rounded-xl text-xs font-medium border border-[#DDE4E1] dark:border-[#2E3A44] text-[#4C5F6B] dark:text-[#B0C2C6] hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
                    >
                      Close
                    </button>
                    <Link
                      to={connected ? selectedTech.actionRoute : '/login'}
                      onClick={() => setSelectedTech(null)}
                      className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2 rounded-xl text-xs font-medium bg-[#0284C7] hover:bg-[#0369A1] text-white shadow-sm transition-colors"
                    >
                      <span>
                        {connected ? selectedTech.actionLabel : 'Connect Workspace to Access'}
                      </span>
                      <ArrowRight size={13} />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ─── Interactive Platform Architecture Modal ─── */}
      {platformModalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
          onClick={() => setPlatformModalOpen(false)}
        >
          <div
            className="relative w-full max-w-4xl max-h-[90vh] flex flex-col rounded-3xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#1C252C] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="p-6 sm:p-8 border-b border-[#DDE4E1] dark:border-[#2E3A44] flex items-start justify-between gap-4 bg-[#F6F4EE]/50 dark:bg-[#151D23]/50">
              <div className="space-y-1.5">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-medium bg-[#0284C7]/10 text-[#0284C7] dark:text-[#38BDF8] border border-[#0284C7]/20">
                  <ShieldCheck size={13} />
                  <span>EVALFORGE PLATFORM OPERATING SYSTEM</span>
                </div>
                <h3 className="text-2xl sm:text-3xl font-sans font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                  Enterprise AI Evaluation Platform
                </h3>
                <p className="text-xs sm:text-sm text-[#4C5F6B] dark:text-[#B0C2C6] max-w-2xl font-normal">
                  A high-throughput, deterministic evaluation runtime for AI engineers. Enforce
                  statistical rigor, multi-model consensus, and automated quality gates across LLM
                  pipelines.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setPlatformModalOpen(false)}
                className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 text-[#7E939C] hover:text-[#2E3A44] dark:hover:text-[#F6F4EE] transition-colors"
                aria-label="Close modal"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body: Scrollable */}
            <div className="p-6 sm:p-8 overflow-y-auto space-y-6">
              {/* 4 Pillars Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#F6F4EE]/40 dark:bg-[#202A32]/40 space-y-2">
                  <div className="flex items-center gap-2.5 text-[#0284C7] dark:text-[#38BDF8]">
                    <div className="w-8 h-8 rounded-lg bg-[#0284C7]/10 flex items-center justify-center">
                      <Cpu size={16} />
                    </div>
                    <span className="font-semibold text-sm text-[#2E3A44] dark:text-[#F6F4EE]">
                      Deterministic Evaluation Engine
                    </span>
                  </div>
                  <p className="text-xs text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed">
                    Custom G-Eval rubrics, exact match, semantic embeddings, context recall, and
                    deterministic assertion scripts for LLM and RAG verification.
                  </p>
                </div>

                <div className="p-4 rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#F6F4EE]/40 dark:bg-[#202A32]/40 space-y-2">
                  <div className="flex items-center gap-2.5 text-[#0284C7] dark:text-[#38BDF8]">
                    <div className="w-8 h-8 rounded-lg bg-[#0284C7]/10 flex items-center justify-center">
                      <Gauge size={16} />
                    </div>
                    <span className="font-semibold text-sm text-[#2E3A44] dark:text-[#F6F4EE]">
                      Sovereign Judge Matrix
                    </span>
                  </div>
                  <p className="text-xs text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed">
                    Unified routing across OpenAI (GPT-4o), Anthropic (Claude 3.5), Google (Gemini
                    1.5), and private self-hosted models (DeepSeek, Llama).
                  </p>
                </div>

                <div className="p-4 rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#F6F4EE]/40 dark:bg-[#202A32]/40 space-y-2">
                  <div className="flex items-center gap-2.5 text-[#0284C7] dark:text-[#38BDF8]">
                    <div className="w-8 h-8 rounded-lg bg-[#0284C7]/10 flex items-center justify-center">
                      <Zap size={16} />
                    </div>
                    <span className="font-semibold text-sm text-[#2E3A44] dark:text-[#F6F4EE]">
                      Distributed Worker Mesh
                    </span>
                  </div>
                  <p className="text-xs text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed">
                    Asynchronous task execution capable of evaluating 100k+ samples concurrently
                    with real-time SSE progress streaming and automated retries.
                  </p>
                </div>

                <div className="p-4 rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#F6F4EE]/40 dark:bg-[#202A32]/40 space-y-2">
                  <div className="flex items-center gap-2.5 text-[#0284C7] dark:text-[#38BDF8]">
                    <div className="w-8 h-8 rounded-lg bg-[#0284C7]/10 flex items-center justify-center">
                      <Terminal size={16} />
                    </div>
                    <span className="font-semibold text-sm text-[#2E3A44] dark:text-[#F6F4EE]">
                      Developer SDK & MCP Server
                    </span>
                  </div>
                  <p className="text-xs text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed">
                    Native Model Context Protocol (MCP) server, standalone terminal CLI,
                    Python/TypeScript SDKs, and GitHub Actions regression gates.
                  </p>
                </div>
              </div>

              {/* Platform Metrics Bar */}
              <div className="p-4 rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#F6F4EE] dark:bg-[#182026] grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-lg sm:text-xl font-mono font-semibold text-[#0284C7] dark:text-[#38BDF8]">
                    99.98%
                  </div>
                  <div className="text-[11px] text-[#7E939C] uppercase tracking-wider mt-0.5">
                    Platform SLA
                  </div>
                </div>
                <div>
                  <div className="text-lg sm:text-xl font-mono font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                    &lt; 240ms
                  </div>
                  <div className="text-[11px] text-[#7E939C] uppercase tracking-wider mt-0.5">
                    P95 Eval Latency
                  </div>
                </div>
                <div>
                  <div className="text-lg sm:text-xl font-mono font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                    100k+
                  </div>
                  <div className="text-[11px] text-[#7E939C] uppercase tracking-wider mt-0.5">
                    Parallel Concurrency
                  </div>
                </div>
                <div>
                  <div className="text-lg sm:text-xl font-mono font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                    Zero Data
                  </div>
                  <div className="text-[11px] text-[#7E939C] uppercase tracking-wider mt-0.5">
                    Retention Mode
                  </div>
                </div>
              </div>

              {/* Quick Action Navigation Links */}
              <div className="space-y-2">
                <div className="text-xs font-mono uppercase tracking-wider text-[#7E939C]">
                  Explore In Depth
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setPlatformModalOpen(false);
                      const el = document.getElementById('capabilities');
                      if (el) el.scrollIntoView({ behavior: 'smooth' });
                    }}
                    className="p-3 text-left rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] hover:border-[#0284C7] dark:hover:border-[#38BDF8] bg-white dark:bg-[#202A32] text-xs font-medium text-[#2E3A44] dark:text-[#F6F4EE] transition-colors flex items-center justify-between cursor-pointer"
                  >
                    <span>6 Core Capabilities</span>
                    <ArrowRight size={13} className="text-[#0284C7]" />
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setPlatformModalOpen(false);
                      const el = document.getElementById('code');
                      if (el) el.scrollIntoView({ behavior: 'smooth' });
                      setActiveCodeTab('simulator');
                      runSimulation();
                    }}
                    className="p-3 text-left rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] hover:border-[#0284C7] dark:hover:border-[#38BDF8] bg-white dark:bg-[#202A32] text-xs font-medium text-[#2E3A44] dark:text-[#F6F4EE] transition-colors flex items-center justify-between cursor-pointer"
                  >
                    <span>Launch Live Simulator ▶</span>
                    <ArrowRight size={13} className="text-[#0284C7]" />
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setPlatformModalOpen(false);
                      const el = document.getElementById('benchmarks');
                      if (el) el.scrollIntoView({ behavior: 'smooth' });
                    }}
                    className="p-3 text-left rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] hover:border-[#0284C7] dark:hover:border-[#38BDF8] bg-white dark:bg-[#202A32] text-xs font-medium text-[#2E3A44] dark:text-[#F6F4EE] transition-colors flex items-center justify-between cursor-pointer"
                  >
                    <span>Sovereign Judge Matrix</span>
                    <ArrowRight size={13} className="text-[#0284C7]" />
                  </button>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-[#DDE4E1] dark:border-[#2E3A44] flex flex-col sm:flex-row items-center justify-between gap-4 bg-[#F6F4EE]/40 dark:bg-[#151D23]/40">
              <span className="text-xs text-[#7E939C]">
                Ready to benchmark and validate your production models?
              </span>
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <button
                  type="button"
                  onClick={() => setPlatformModalOpen(false)}
                  className="w-full sm:w-auto px-4 py-2 rounded-xl text-xs font-medium border border-[#DDE4E1] dark:border-[#2E3A44] text-[#4C5F6B] dark:text-[#B0C2C6] hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
                >
                  Close
                </button>
                <Link
                  to={connected ? '/overview' : '/login'}
                  onClick={() => setPlatformModalOpen(false)}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-[#0284C7] hover:bg-[#0369A1] text-white shadow-sm transition-colors uppercase tracking-wider"
                >
                  <span>{connected ? 'Enter Workspace' : 'Launch Workspace'}</span>
                  <ArrowRight size={13} />
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ─── Why Engineering Teams Choose EvalForge (Coursera Style Testimonials) ─── */}
      <section className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44] bg-[#EFECE4]/20 dark:bg-[#1C252C]/20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-[#0284C7]/10 text-[#0284C7] dark:text-[#38BDF8] border border-[#0284C7]/20 mb-1">
              <ShieldCheck size={12} />
              <span>Enterprise Rigor & Production Trust</span>
            </div>
            <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C]">
              Social Proof & Industry Evidence
            </div>
            <h2 className="font-sans text-4xl sm:text-5xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE]">
              Why AI teams choose EvalForge
            </h2>
            <p className="text-sm text-[#4C5F6B] dark:text-[#B0C2C6]">
              From high-growth AI startups to regulated financial institutions, teams trust
              EvalForge to benchmark reasoning, prevent hallucinations, and deploy LLMs with
              empirical certainty.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {TESTIMONIALS.map((item) => (
              <div
                key={item.name}
                className="p-6 rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#202A32] shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-6"
              >
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <img
                      src={item.avatar}
                      alt={item.name}
                      className="w-12 h-12 rounded-full object-cover border border-[#DDE4E1] dark:border-[#4C5F6B]"
                    />
                    <div>
                      <div className="font-semibold text-sm text-[#2E3A44] dark:text-[#F6F4EE]">
                        {item.name}
                      </div>
                      <div className="text-[11px] text-[#7E939C] leading-tight mt-0.5">
                        {item.role}
                      </div>
                      <div className="text-[10px] font-mono text-[#0284C7] dark:text-[#38BDF8] mt-0.5">
                        {item.company}
                      </div>
                    </div>
                  </div>
                  <p className="text-xs text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed font-sans">
                    &quot;{item.quote}&quot;
                  </p>
                </div>

                <div className="pt-3 border-t border-[#DDE4E1] dark:border-[#2E3A44] flex items-center justify-between text-[11px] font-mono text-[#7E939C]">
                  <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
                    <CheckCircle2 size={12} />
                    <span>Verified Production User</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Frequently Asked Questions (Coursera Style Accordion) ─── */}
      <section className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center max-w-xl mx-auto mb-14 space-y-3">
            <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C]">
              Technical Inquiries
            </div>
            <h2 className="font-sans text-3xl sm:text-4xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE]">
              Frequently asked questions
            </h2>
            <p className="text-xs sm:text-sm text-[#4C5F6B] dark:text-[#B0C2C6]">
              Clear answers on deterministic scoring, sovereign judge mechanics, air-gapped
              deployments, and CI/CD automation.
            </p>
          </div>

          <div className="space-y-3">
            {FAQ_ITEMS.map((faq, idx) => {
              const isOpen = expandedFaq === idx;
              return (
                <div
                  key={faq.q}
                  className="rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#202A32] overflow-hidden transition-all shadow-sm"
                >
                  <button
                    type="button"
                    onClick={() => setExpandedFaq(isOpen ? null : idx)}
                    className="w-full p-5 sm:p-6 text-left flex items-center justify-between gap-4 cursor-pointer hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors"
                    aria-expanded={isOpen}
                  >
                    <span className="font-medium text-sm sm:text-base text-[#2E3A44] dark:text-[#F6F4EE] leading-snug">
                      {faq.q}
                    </span>
                    <span className="p-1 rounded-full bg-[#EFECE4] dark:bg-[#1C252C] text-[#4C5F6B] dark:text-[#B0C2C6] shrink-0">
                      {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </span>
                  </button>

                  {isOpen && (
                    <div className="px-5 sm:px-6 pb-6 pt-1 text-xs sm:text-sm text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed border-t border-[#DDE4E1]/60 dark:border-[#2E3A44]/60 bg-[#F6F4EE]/30 dark:bg-[#182026]/40 animate-in fade-in duration-200">
                      {faq.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ─── Final Editorial Call-To-Action ─── */}
      <section className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
        <div className="max-w-5xl mx-auto px-6 text-center space-y-8">
          <div className="w-16 h-16 mx-auto flex items-center justify-center transition-transform duration-300 hover:scale-110">
            <img
              src="/logo.png"
              alt="EvalForge Emblem"
              className="w-16 h-16 object-contain drop-shadow-md"
            />
          </div>

          <h2 className="font-sans text-4xl sm:text-6xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE]">
            Ready to evaluate <br />
            <span className="text-[#0369A1] dark:text-[#38BDF8]">with complete confidence?</span>
          </h2>

          <p className="text-base sm:text-lg text-[#4C5F6B] dark:text-[#B0C2C6] max-w-xl mx-auto">
            Connect your workspace, import your first dataset, and benchmark your models today.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              to={connected ? '/overview' : '/login'}
              className="px-8 py-4 rounded-full bg-[#0284C7] hover:bg-[#0369A1] text-white text-sm font-semibold uppercase tracking-wider transition-all duration-200 shadow-md cursor-pointer"
            >
              {connected ? 'Enter Workspace Now →' : 'Launch Workspace →'}
            </Link>
            <a
              href="https://github.com/hardikkaurani/Eval-Forge/blob/main/docs/api.md"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 rounded-full border border-[#B0C2C6] dark:border-[#4C5F6B] hover:border-[#2E3A44] text-sm font-medium text-[#2E3A44] dark:text-[#F6F4EE] transition-colors cursor-pointer"
            >
              Read Documentation ↗
            </a>
          </div>
        </div>
      </section>

      {/* ─── Coursera-Grade Multi-Column Footer ─── */}
      <footer className="pt-16 pb-12 bg-[#EFECE4] dark:bg-[#151D23] text-xs text-[#7E939C]">
        <div className="max-w-7xl mx-auto px-6 space-y-12">
          {/* Quick Install Command Bar */}
          <div className="p-6 rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#1C252C] flex flex-col md:flex-row items-center justify-between gap-6 shadow-sm">
            <div className="space-y-1 text-center md:text-left">
              <div className="text-xs font-mono font-semibold uppercase tracking-wider text-[#2E3A44] dark:text-[#F6F4EE]">
                Developer SDKs & Package Managers
              </div>
              <div className="text-xs text-[#4C5F6B] dark:text-[#B0C2C6]">
                Install into your Python, Node.js, or container environment in seconds.
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-3 font-mono text-[11px]">
              <button
                type="button"
                onClick={() => handleCopyBadge('pip install evalforge-sdk', 'pip')}
                className="px-3 py-2 rounded-xl bg-[#F6F4EE] dark:bg-[#202A32] border border-[#DDE4E1] dark:border-[#2E3A44] hover:border-[#0284C7] text-[#2E3A44] dark:text-[#F6F4EE] flex items-center gap-2 transition-colors cursor-pointer"
                title="Click to copy pip command"
              >
                <span>pip install evalforge-sdk</span>
                {copiedBadge === 'pip' ? (
                  <Check size={12} className="text-emerald-500" />
                ) : (
                  <Copy size={12} className="text-[#7E939C]" />
                )}
              </button>

              <button
                type="button"
                onClick={() => handleCopyBadge('npm i @evalforge/client', 'npm')}
                className="px-3 py-2 rounded-xl bg-[#F6F4EE] dark:bg-[#202A32] border border-[#DDE4E1] dark:border-[#2E3A44] hover:border-[#0284C7] text-[#2E3A44] dark:text-[#F6F4EE] flex items-center gap-2 transition-colors cursor-pointer"
                title="Click to copy npm command"
              >
                <span>npm i @evalforge/client</span>
                {copiedBadge === 'npm' ? (
                  <Check size={12} className="text-emerald-500" />
                ) : (
                  <Copy size={12} className="text-[#7E939C]" />
                )}
              </button>

              <button
                type="button"
                onClick={() => handleCopyBadge('docker pull evalforge/engine:v1', 'docker')}
                className="px-3 py-2 rounded-xl bg-[#F6F4EE] dark:bg-[#202A32] border border-[#DDE4E1] dark:border-[#2E3A44] hover:border-[#0284C7] text-[#2E3A44] dark:text-[#F6F4EE] flex items-center gap-2 transition-colors cursor-pointer"
                title="Click to copy docker command"
              >
                <span>docker pull evalforge/engine</span>
                {copiedBadge === 'docker' ? (
                  <Check size={12} className="text-emerald-500" />
                ) : (
                  <Copy size={12} className="text-[#7E939C]" />
                )}
              </button>
            </div>
          </div>

          {/* 4 Multi-Column Grid (Coursera Structure) */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 sm:gap-12">
            {/* Column 1: EvalForge Platform */}
            <div className="space-y-3 font-sans">
              <div className="font-semibold text-sm text-[#2E3A44] dark:text-[#F6F4EE]">
                EvalForge Platform
              </div>
              <ul className="space-y-2.5">
                <li>
                  <button
                    type="button"
                    onClick={() => {
                      setPlatformModalOpen(true);
                      const el = document.getElementById('platform');
                      if (el) el.scrollIntoView({ behavior: 'smooth' });
                    }}
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors cursor-pointer text-left"
                  >
                    Platform Architecture
                  </button>
                </li>
                <li>
                  <a
                    href="#capabilities"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Deterministic Evaluation Engine
                  </a>
                </li>
                <li>
                  <a
                    href="#benchmarks"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Sovereign Judge Matrix
                  </a>
                </li>
                <li>
                  <a
                    href="#capabilities"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    RAG Triad Grounding
                  </a>
                </li>
                <li>
                  <Link
                    to={connected ? '/datasets' : '/login'}
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Golden Dataset Vault
                  </Link>
                </li>
                <li>
                  <a
                    href="#architecture"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Infrastructure Topology
                  </a>
                </li>
                <li>
                  <Link
                    to={connected ? '/settings/system' : '/login'}
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Cluster Telemetry & Health
                  </Link>
                </li>
              </ul>
            </div>

            {/* Column 2: Developer Ecosystem */}
            <div className="space-y-3 font-sans">
              <div className="font-semibold text-sm text-[#2E3A44] dark:text-[#F6F4EE]">
                Developer Ecosystem
              </div>
              <ul className="space-y-2.5">
                <li>
                  <a
                    href="https://github.com/hardikkaurani/Eval-Forge/blob/main/docs/api.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Python SDK Reference
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/hardikkaurani/Eval-Forge/blob/main/docs/cli.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Standalone Terminal CLI
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/hardikkaurani/Eval-Forge/blob/main/docs/mcp.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Anthropic MCP Server
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/hardikkaurani/Eval-Forge/blob/main/docs/evaluations.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    OpenAPI 3.1 REST Specs
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/hardikkaurani/Eval-Forge/actions"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    GitHub Actions CI Runner
                  </a>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => {
                      const el = document.getElementById('code');
                      if (el) el.scrollIntoView({ behavior: 'smooth' });
                      setActiveCodeTab('simulator');
                      runSimulation();
                    }}
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors cursor-pointer text-left"
                  >
                    Live Evaluation Simulator ▶
                  </button>
                </li>
                <li>
                  <Link
                    to={connected ? '/settings/guide' : '/login'}
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Developer Integration Guide
                  </Link>
                </li>
              </ul>
            </div>

            {/* Column 3: Resources & Research */}
            <div className="space-y-3 font-sans">
              <div className="font-semibold text-sm text-[#2E3A44] dark:text-[#F6F4EE]">
                Resources & Research
              </div>
              <ul className="space-y-2.5">
                <li>
                  <button
                    type="button"
                    onClick={() => setActiveDocModal(LEGAL_DOCS.whitepaper)}
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors cursor-pointer text-left flex items-center gap-1.5"
                  >
                    <span>Technical Whitepaper</span>
                    <FileText size={11} className="text-[#0284C7]" />
                  </button>
                </li>
                <li>
                  <a
                    href="https://github.com/hardikkaurani/Eval-Forge/blob/main/docs/ARCHITECTURE.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Architecture Specifications
                  </a>
                </li>
                <li>
                  <a
                    href="#workflow"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    G-Eval & CoT Methodology
                  </a>
                </li>
                <li>
                  <a
                    href="#capabilities"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Hallucination Mitigation Playbook
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/hardikkaurani/Eval-Forge/releases"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    v1.0.0 Release Notes
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/hardikkaurani/Eval-Forge"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    GitHub Discussions
                  </a>
                </li>
              </ul>
            </div>

            {/* Column 4: Governance & Legal */}
            <div className="space-y-3 font-sans">
              <div className="font-semibold text-sm text-[#2E3A44] dark:text-[#F6F4EE]">
                Governance & Legal
              </div>
              <ul className="space-y-2.5">
                <li>
                  <button
                    type="button"
                    onClick={() => setActiveDocModal(LEGAL_DOCS.privacy)}
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors cursor-pointer text-left flex items-center gap-1.5"
                  >
                    <span>Zero Data Retention Policy</span>
                    <ShieldCheck size={11} className="text-[#0284C7]" />
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => setActiveDocModal(LEGAL_DOCS.security)}
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors cursor-pointer text-left flex items-center gap-1.5"
                  >
                    <span>Security & Vulnerability Disclosure</span>
                    <ShieldCheck size={11} className="text-[#0284C7]" />
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => setActiveDocModal(LEGAL_DOCS.terms)}
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors cursor-pointer text-left flex items-center gap-1.5"
                  >
                    <span>Terms of Infrastructure</span>
                    <FileText size={11} className="text-[#0284C7]" />
                  </button>
                </li>
                <li>
                  <a
                    href="https://github.com/hardikkaurani/Eval-Forge/blob/main/LICENSE"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    MIT Open Source License
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/hardikkaurani/Eval-Forge/security/policy"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Security Advisory Program
                  </a>
                </li>
                <li>
                  <Link
                    to={connected ? '/overview' : '/login'}
                    className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                  >
                    Enterprise VPC Inquiries
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Copyright & Social Bar */}
          <div className="pt-8 border-t border-[#DDE4E1] dark:border-[#2E3A44] flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <img src="/logo.png" alt="EvalForge" className="w-7 h-7 object-contain" />
              <span className="font-sans text-base font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                EvalForge.
              </span>
              <span className="text-[#B0C2C6]">·</span>
              <span className="text-xs">
                © 2026 EvalForge Inc. All rights reserved. Deterministic AI Quality & Benchmark
                Infrastructure.
              </span>
            </div>

            <div className="flex items-center gap-4 text-[#4C5F6B] dark:text-[#B0C2C6]">
              <a
                href="https://github.com/hardikkaurani/Eval-Forge"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                aria-label="GitHub Repository"
                title="GitHub"
              >
                <Github size={16} />
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                aria-label="LinkedIn"
                title="LinkedIn"
              >
                <Linkedin size={16} />
              </a>
              <a
                href="https://x.com"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                aria-label="Twitter / X"
                title="Twitter / X"
              >
                <Twitter size={16} />
              </a>
              <a
                href="https://github.com/hardikkaurani/Eval-Forge/discussions"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                aria-label="Discussions"
                title="Community Discussions"
              >
                <MessageSquare size={16} />
              </a>
              <a
                href="https://github.com/hardikkaurani/Eval-Forge/blob/main/docs/api.md"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
                aria-label="Documentation"
                title="API Documentation"
              >
                <FileText size={16} />
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* ─── Interactive Document / File Viewer Modal ─── */}
      {activeDocModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
          onClick={() => setActiveDocModal(null)}
        >
          <div
            className="relative w-full max-w-3xl max-h-[85vh] flex flex-col rounded-3xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#1C252C] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="p-6 sm:p-8 border-b border-[#DDE4E1] dark:border-[#2E3A44] flex items-start justify-between gap-4 bg-[#F6F4EE]/50 dark:bg-[#151D23]/50">
              <div className="space-y-1">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-mono font-medium bg-[#0284C7]/10 text-[#0284C7] dark:text-[#38BDF8] border border-[#0284C7]/20">
                  <FileText size={12} />
                  <span>{activeDocModal.badge}</span>
                </div>
                <h3 className="text-xl sm:text-2xl font-sans font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                  {activeDocModal.title}
                </h3>
                <div className="text-[11px] font-mono text-[#7E939C]">
                  Effective Date: {activeDocModal.lastUpdated} · EvalForge Foundation Governance
                </div>
              </div>
              <button
                type="button"
                onClick={() => setActiveDocModal(null)}
                className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 text-[#7E939C] hover:text-[#2E3A44] dark:hover:text-[#F6F4EE] transition-colors cursor-pointer"
                aria-label="Close document modal"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body: Scrollable Document Content */}
            <div className="p-6 sm:p-8 overflow-y-auto space-y-6 text-xs sm:text-sm text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed font-sans">
              {activeDocModal.content.map((sec) => (
                <div key={sec.heading} className="space-y-2">
                  <h4 className="font-semibold text-sm sm:text-base text-[#2E3A44] dark:text-[#F6F4EE]">
                    {sec.heading}
                  </h4>
                  <p>{sec.text}</p>
                </div>
              ))}
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-[#DDE4E1] dark:border-[#2E3A44] flex items-center justify-between gap-4 bg-[#F6F4EE]/40 dark:bg-[#151D23]/40">
              <span className="text-[11px] text-[#7E939C] font-mono">
                Cryptographically audited for enterprise VPC standards.
              </span>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setActiveDocModal(null)}
                  className="px-5 py-2.5 rounded-xl text-xs font-medium border border-[#DDE4E1] dark:border-[#2E3A44] text-[#4C5F6B] dark:text-[#B0C2C6] hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
                >
                  Close Document
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
