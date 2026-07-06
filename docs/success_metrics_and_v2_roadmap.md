# EvalForge v1.0.0 Success Metrics & Version 2.0 Roadmap

This document establishes the telemetry metrics for project health and lists experimental concepts for the next major version release.

---

## 1. Project Success Metrics

To monitor the adoption, utility, and health of the open-source community, we track key metrics across three domains:

### 1.1 Developer Adoption & Community
- **GitHub Stars**: Target 1,000+ stars within the first 6 months. Represents initial discoverability and developer interest.
- **Forks**: Target 150+ forks. Indicates developers extending EvalForge or preparing pull requests.
- **Active Contributors**: Target 20+ active external contributors. Reflects open-source sustainability.
- **Discord/Community Members**: Target 500+ developers participating in support discussions.

### 1.2 Engineering & Operational Telemetry
- **Deployments (Active Instances)**: Number of unique active self-hosted installations pinging update registries. Target 200+ instances.
- **Total Evaluations Completed**: Count of individual test cases evaluated. Target 10M+ evaluations.
- **API Request Throughput**: Average number of public API calls made to `/api/v1/public`.
- **WebSocket Connection Success Rate**: Target 99.9% uptime for real-time progress events.

---

## 2. Version 2.0 Roadmap (Concepts Only)

The following areas represent high-priority research and architectural directions. These are ideas only and are **not** implemented in the current release.

### 2.1 Autonomous Agentic Evaluations
- **Agent Sandbox Execution**: Launch the candidate agent in a secure, isolated container. Let a judicial agent play the role of a user, attempting to trip up or jailbreak the target agent.
- **Multi-turn Dialogue Evaluation**: Evaluate the coherence, context memory, and task alignment of an LLM across multiple conversational turns, scoring dialogue flow.

### 2.2 Local Edge Judges (Zero-Cost Evals)
- **Local Model Wrappers**: Support zero-cost local evaluations by running lightweight judge models (e.g. Qwen-2.5-Coder-7B) on developer machines via Ollama.
- **WebGPU Judges**: Experiment with running ONNX-compiled tiny classifiers directly inside the client's browser web app for lightning-fast visual and linguistic validation.

### 2.3 Deep GitOps Integrations
- **CI Pull Request Comments**: Automatically post rich markdown reports as comments inside pull requests whenever prompt or dataset updates are made, showing exact delta charts.
- **Local Git Hooks**: Provide pre-commit hooks to block code changes if local evaluation checks on prompt rubrics fail basic compliance tests.
