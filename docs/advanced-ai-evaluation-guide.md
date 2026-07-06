# Advanced AI Evaluation, RAG & Enterprise Intelligence Guide

This guide describes how to configure, execute, and monitor advanced evaluations for Retrieval-Augmented Generation (RAG), Agentic workflows, Safety, Security, and Regression tracking inside EvalForge.

---

## 1. RAG Evaluation Metrics

RAG pipelines are evaluated across multiple retrieval and generation dimensions:

* **Context Precision**: The fraction of retrieved context snippets relevant to answering the query.
* **Context Recall**: The proportion of ground-truth information successfully captured in the retrieved context.
* **Answer Relevancy**: Semantic similarity and relevance of the assistant response to the user's question.
* **Faithfulness / Groundedness**: Verification that the generated answer is completely backed by the retrieved context, without introducing fabricated facts.
* **Citation & Attribution**: Checks whether sources are cited correctly in the text and if resources are correctly mapped back to their original reference documents.

---

## 2. Hallucination Detection Engine

The Hallucination Engine audits model responses against grounding context snippets to detect:
* **Unsupported Claims**: Statements in the output that have no corresponding information in the source material.
* **Fabricated Facts**: Generation of synthetic names, dates, or attributes not present in the reference documents.
* **Contradictions**: Assertions in the output directly conflicting with claims in the context documents.

---

## 3. Safety & Toxicity Auditing

Safety reviews output generations for compliance with acceptable use policies:
* **Toxicity**: Insults, offensive language, or hate speech patterns.
* **Violence & Harassment**: Expressions of violence, bullying, self-harm encouragement, or adult-only content.
* **Illegal Activity**: Direct or indirect instructions regarding hacking, piracy, or illicit activities.

---

## 4. Security & Prompt Injection Mitigation

Security evaluations monitor prompt vulnerabilities and potential data leakage vectors:
* **Jailbreaks**: Direct adversarial overrides attempting to place the model in developer or unaligned modes.
* **Prompt Injections**: Indirect manipulation where untrusted context instructions override the system template.
* **PII & Secret Leakage**: Auto-redaction audits searching for credentials, keys (e.g. `sk-`), emails, and phone numbers in model outputs.

---

## 5. Agent & Multi-Turn Conversation Evaluation

Evaluates memory, coherence, planning, and task completion in agentic loops:
* **Planning Quality**: The logical progression of tasks and tool selections.
* **Memory Retention**: Consistency of context and facts over multi-turn sessions.
* **Tool Calling Accuracy**:
  * Function selection precision.
  * Correct formatting and typed parameters.
  * Resiliency, retry counts, and error recovery behavior.

---

## 6. Enterprise Policy Engine

Define custom organization guardrails:
* **Prohibited Topics**: Restrict discussions to specific business domains.
* **Guardrail Enforcement**: Reject prompt requests or sanitize outputs violating company compliance templates.

---

## 7. Model Regression Testing

Track model degradation across release cycles:
* **Base vs. Candidate Comparisons**: Run automated checks between base runs and new releases.
* **Degradation Detection**: Automatically trigger alerts if success rates decrease by more than a defined threshold (default: > 2%) or average evaluation score declines.
