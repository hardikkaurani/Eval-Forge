# Evaluation Engine Guide

The EvalForge evaluation engine is a modular pipeline for scoring model outputs with interchangeable providers, judges, metrics, and rubrics.

## Core flow

1. Validate request payloads and configuration.
2. Resolve provider, judge, and rubric implementations from the registry.
3. Render prompt templates with the prompt engine.
4. Execute the judge through the configured provider.
5. Normalize and aggregate scores through the metrics engine.
6. Persist run, result, rubric score, and provider metadata records.

## Supported evaluation modes

- LLM-as-a-Judge
- G-Eval
- Pairwise comparison
- Reference-based scoring
- Custom rubric scoring

## Design notes

- Providers are replaceable without changing business logic.
- Judges are selected through registry lookup rather than branching.
- Batch runs isolate failures and continue processing remaining cases.
- Prompt templates are versioned and can be overridden at runtime.

## Where to look in code

- `backend/app/evaluation/pipelines/pipeline.py`
- `backend/app/evaluation/services/evaluation.py`
- `backend/app/evaluation/registry/registry.py`
- `backend/app/evaluation/prompts/engine.py`
