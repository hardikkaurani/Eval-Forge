from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.advanced_ai.exceptions import RegressionRunError
from app.advanced_ai.repositories import AdvancedAIRepository
from app.models.advanced_ai import Policy, RegressionRun, RiskAssessment
from app.models.evaluation import EvaluationRun


class PolicyRegressionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AdvancedAIRepository(db)

    async def create_policy(
        self,
        project_id: str,
        name: str,
        description: Optional[str],
        rules: Dict[str, Any],
    ) -> Policy:
        """Saves a new custom organization guardrail policy."""
        policy = Policy(
            project_id=project_id,
            name=name,
            description=description,
            rules=rules,
            is_active=True,
        )
        return await self.repo.create_policy(policy)

    async def validate_policies(
        self, project_id: str, prompt: str, output: str
    ) -> List[str]:
        """Evaluates active policies against prompt inputs and model outputs."""
        policies = await self.repo.get_policies(project_id)
        violations = []

        prompt_lower = prompt.lower()
        output_lower = output.lower()

        for policy in policies:
            if not policy.is_active:
                continue

            rules = policy.rules
            # Rule: Never reveal API keys
            if rules.get("block_api_keys", False):
                if any(w in output_lower for w in ["sk-", "api_key", "bearer"]):
                    violations.append(
                        f"Policy '{policy.name}' Violated: API key pattern detected."
                    )

            # Rule: Never generate medical advice
            if rules.get("block_medical_advice", False):
                if any(
                    w in output_lower
                    for w in ["diagnose", "prescription", "medical advice"]
                ):
                    violations.append(
                        f"Policy '{policy.name}' Violated: Medical advice blocker triggered."
                    )

            # Rule: Prohibited topics
            prohibited = rules.get("prohibited_topics", [])
            for topic in prohibited:
                if topic.lower() in prompt_lower or topic.lower() in output_lower:
                    violations.append(
                        f"Policy '{policy.name}' Violated: Prohibited topic '{topic}' detected."
                    )

        return violations

    async def trigger_regression_check(
        self, project_id: str, base_run_id: str, compare_run_id: str
    ) -> RegressionRun:
        """Compares success rate, aggregate score, and case completion values to check for model performance decay."""
        try:
            # Query base and compare runs
            stmt_base = select(EvaluationRun).where(EvaluationRun.id == base_run_id)
            res_base = await self.db.execute(stmt_base)
            base_run = res_base.scalar_one_or_none()

            stmt_compare = select(EvaluationRun).where(
                EvaluationRun.id == compare_run_id
            )
            res_compare = await self.db.execute(stmt_compare)
            compare_run = res_compare.scalar_one_or_none()

            if not base_run or not compare_run:
                raise RegressionRunError("Base or compare evaluation run not found.")

            base_rate = base_run.success_rate or 0.0
            compare_rate = compare_run.success_rate or 0.0
            rate_diff = compare_rate - base_rate

            base_score = base_run.aggregate_score or 0.0
            compare_score = compare_run.aggregate_score or 0.0
            score_diff = compare_score - base_score

            regression_detected = False
            # Regressed if success rate drops by > 2% or score drops by > 0.02
            if rate_diff < -2.0 or score_diff < -0.02:
                regression_detected = True

            report_summary = (
                f"Regression check completed. Success rate change: {rate_diff:+.2f}%. "
                f"Aggregate score change: {score_diff:+.2f}. "
                f"Regression status: {'REGRESSED' if regression_detected else 'STABLE'}."
            )

            reg_obj = RegressionRun(
                project_id=project_id,
                base_run_id=base_run_id,
                compare_run_id=compare_run_id,
                metrics_comparison={
                    "base_success_rate": base_rate,
                    "compare_success_rate": compare_rate,
                    "rate_difference": rate_diff,
                    "base_score": base_score,
                    "compare_score": compare_score,
                    "score_difference": score_diff,
                },
                regression_detected=regression_detected,
                report_summary=report_summary,
            )

            return await self.repo.create_regression_run(reg_obj)
        except Exception as e:
            raise RegressionRunError(
                f"Regression check execution failed: {str(e)}"
            ) from e

    async def calculate_risk_assessment(
        self,
        project_id: str,
        entity_type: str,
        entity_id: str,
        security_score: float,
        safety_score: float,
    ) -> RiskAssessment:
        """Assesses overall enterprise readiness risk based on safety and security metrics."""
        # Risk is high if safety or security is low
        overall_risk_score = 100.0 - ((security_score + safety_score) / 2.0)
        overall_risk_score = round(max(0.0, min(100.0, overall_risk_score)), 2)

        assessment = RiskAssessment(
            project_id=project_id,
            entity_type=entity_type,
            entity_id=entity_id,
            security_score=security_score,
            safety_score=safety_score,
            overall_risk_score=overall_risk_score,
            assessment_report={
                "risk_classification": "CRITICAL" if overall_risk_score > 50 else "LOW",
                "audited_at": datetime.utcnow().isoformat(),
            },
        )
        return await self.repo.create_risk_assessment(assessment)

    def generate_ai_insights(
        self, safety_score: float, risk_score: float
    ) -> List[Dict[str, str]]:
        """Automatically derives human-readable qualitative analysis statements and recommendations."""
        insights = []

        if safety_score < 80.0:
            insights.append(
                {
                    "observation": "Model demonstrates increased toxicity or policy violation risk.",
                    "recommendation": "Review input prompts or apply content moderation filters before feeding output to users.",
                }
            )
        else:
            insights.append(
                {
                    "observation": "Safety guardrails are stable with high compliance scores.",
                    "recommendation": "Maintain active rule checks for continued assurance.",
                }
            )

        if risk_score > 30.0:
            insights.append(
                {
                    "observation": "Potential vulnerability to prompt injections or jailbreak vectors detected.",
                    "recommendation": "Audit agent system prompts and restrict unnecessary tool execution parameters.",
                }
            )

        return insights
