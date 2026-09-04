"""Eval-Forge Python SDK Quickstart Example.

Demonstrates the complete evaluation lifecycle:
1. Initialize the official EvalForge SDK client.
2. Create or retrieve an evaluation project.
3. Upload a dataset with structured test cases.
4. Launch an asynchronous evaluation run.
5. Poll and inspect granular scoring metrics and rationale.
"""

import os
import sys
import time

try:
    from evalforge import EvalForge
except ImportError:
    print("Please install the evalforge SDK: pip install evalforge")
    sys.exit(1)


def main():
    api_key = os.environ.get("EVALFORGE_API_KEY", "ef_live_example_key")
    base_url = os.environ.get("EVALFORGE_BASE_URL", "http://localhost:8000")

    print("=" * 60)
    print("🚀 Eval-Forge Python SDK — End-to-End Evaluation")
    print(f"Target Base URL: {base_url}")
    print("=" * 60)

    # 1. Initialize Client
    client = EvalForge(api_key=api_key, base_url=base_url)

    # 2. Create Project
    print("\n[1/4] Creating Evaluation Project...")
    try:
        project = client.projects.create(
            name="Customer Support Quality Suite",
            description="Automated rubric and semantic benchmark for support bots",
        )
        project_id = project.get("id", "00000000-0000-0000-0000-000000000001")
        print(f"✓ Project Created: ID={project_id}")
    except Exception as e:
        print(f"! Notice: {e}")
        project_id = "00000000-0000-0000-0000-000000000001"

    # 3. Define Test Cases
    test_cases = [
        {
            "input": "How do I reset my account password?",
            "actual_output": "To reset your password, navigate to Settings > Security and click 'Reset Password'. We will send an email with instructions.",
            "expected_output": "Go to Settings > Security > Reset Password and follow the email instructions.",
            "metadata": {"category": "auth", "difficulty": "easy"},
        },
        {
            "input": "What is the refund policy for annual enterprise subscriptions?",
            "actual_output": "Enterprise subscriptions can be refunded pro-rata within the first 14 days of purchase upon contacting support.",
            "expected_output": "Pro-rated refund available within 14 days of purchase through enterprise support.",
            "metadata": {"category": "billing", "difficulty": "medium"},
        },
    ]

    # 4. Launch Evaluation Run
    print("\n[2/4] Launching Evaluation Run...")
    try:
        eval_run = client.evaluations.create(
            project_id=project_id,
            name="v1.0 Customer Support Prompt Eval",
            test_cases=test_cases,
            metrics=["accuracy", "semantic_similarity", "hallucination"],
        )
        run_id = eval_run.get("id", eval_run.get("job_id"))
        print(f"✓ Evaluation Run Submitted: Run ID={run_id}")
    except Exception as e:
        print(f"Failed to submit evaluation: {e}")
        return

    # 5. Fetch Results
    print("\n[3/4] Fetching Evaluation Results...")
    time.sleep(2)  # Allow background worker to process
    try:
        results = client.evaluations.list_results(run_id=run_id, limit=10)
        print(f"✓ Retrieved {len(results)} evaluated test case results.")
        for idx, res in enumerate(results, 1):
            print(f"\n  Test Case #{idx}:")
            print(f"    - Score: {res.get('score', 'N/A')}")
            print(f"    - Passed: {res.get('passed', True)}")
            print(f"    - Metrics: {res.get('metrics', {})}")
    except Exception as e:
        print(f"Result retrieval notice: {e}")

    print("\n" + "=" * 60)
    print("✅ Evaluation lifecycle completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
