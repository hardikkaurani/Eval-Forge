---
name: ⚡ Performance Improvement
about: Propose latency, memory, database query, or bundle size optimizations
title: '[PERF]: '
labels: ['performance', 'enhancement']
---

## Description
Summary of the performance bottleneck or resource inefficiency identified.

## Context & Benchmark Metrics
- Current response time / memory footprint / bundle size.
- Target response time / resource reduction.

## Reproduction / Profiling Data
Provide profiling outputs, Flamegraphs, PostgreSQL `EXPLAIN ANALYZE` traces, or Chrome DevTools memory snapshots demonstrating the issue.

## Proposed Optimization
Describe the refactoring or algorithmic improvement.

## Suggested Files
- `backend/app/...`
- `frontend/src/...`

## Acceptance Criteria
- [ ] Benchmark comparison demonstrates measurable improvement.
- [ ] No regression in functional behavior or test coverage.
- [ ] All unit and integration tests pass.
