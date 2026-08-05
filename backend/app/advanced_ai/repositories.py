from typing import Any, Dict, List, Optional

from sqlalchemy import delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.advanced_ai import (
    AgentEvaluation,
    ConversationEvaluation,
    HallucinationReport,
    Policy,
    PromptVersion,
    RAGEvaluation,
    RegressionRun,
    RiskAssessment,
    SafetyEvaluation,
    SecurityEvaluation,
)


class AdvancedAIRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # RAG Evaluation
    async def create_rag_evaluation(self, eval_obj: RAGEvaluation) -> RAGEvaluation:
        self.db.add(eval_obj)
        await self.db.flush()
        return eval_obj

    async def get_rag_evaluations(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[RAGEvaluation]:
        stmt = (
            select(RAGEvaluation)
            .where(RAGEvaluation.project_id == project_id)
            .order_by(desc(RAGEvaluation.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # Hallucination Report
    async def create_hallucination_report(
        self, report: HallucinationReport
    ) -> HallucinationReport:
        self.db.add(report)
        await self.db.flush()
        return report

    async def get_hallucination_reports(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[HallucinationReport]:
        stmt = (
            select(HallucinationReport)
            .where(HallucinationReport.project_id == project_id)
            .order_by(desc(HallucinationReport.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # Safety Evaluation
    async def create_safety_evaluation(
        self, safety: SafetyEvaluation
    ) -> SafetyEvaluation:
        self.db.add(safety)
        await self.db.commit()
        await self.db.refresh(safety)
        return safety


    async def get_safety_evaluations(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[SafetyEvaluation]:
        stmt = (
            select(SafetyEvaluation)
            .where(SafetyEvaluation.project_id == project_id)
            .order_by(desc(SafetyEvaluation.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # Security Evaluation
    async def create_security_evaluation(
        self, security: SecurityEvaluation
    ) -> SecurityEvaluation:
        self.db.add(security)
        await self.db.commit()
        await self.db.refresh(security)
        return security


    async def get_security_evaluations(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[SecurityEvaluation]:
        stmt = (
            select(SecurityEvaluation)
            .where(SecurityEvaluation.project_id == project_id)
            .order_by(desc(SecurityEvaluation.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # Conversation Evaluation
    async def create_conversation_evaluation(
        self, convo: ConversationEvaluation
    ) -> ConversationEvaluation:
        self.db.add(convo)
        await self.db.commit()
        await self.db.refresh(convo)
        return convo

    async def get_conversation_evaluations(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[ConversationEvaluation]:
        stmt = (
            select(ConversationEvaluation)
            .where(ConversationEvaluation.project_id == project_id)
            .order_by(desc(ConversationEvaluation.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # Agent Evaluation
    async def create_agent_evaluation(
        self, agent_eval: AgentEvaluation
    ) -> AgentEvaluation:
        self.db.add(agent_eval)
        await self.db.commit()
        await self.db.refresh(agent_eval)
        return agent_eval

    async def get_agent_evaluations(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[AgentEvaluation]:
        stmt = (
            select(AgentEvaluation)
            .where(AgentEvaluation.project_id == project_id)
            .order_by(desc(AgentEvaluation.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # Policy
    async def create_policy(self, policy: Policy) -> Policy:
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def get_policy(self, policy_id: str) -> Optional[Policy]:
        stmt = select(Policy).where(Policy.id == policy_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_policies(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[Policy]:
        stmt = (
            select(Policy)
            .where(Policy.project_id == project_id)
            .order_by(desc(Policy.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_policy(
        self, policy_id: str, values: Dict[str, Any]
    ) -> Optional[Policy]:
        stmt = (
            update(Policy)
            .where(Policy.id == policy_id)
            .values(**values)
            .returning(Policy)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def delete_policy(self, policy_id: str) -> bool:
        stmt = delete(Policy).where(Policy.id == policy_id)
        res = await self.db.execute(stmt)
        return (res.rowcount or 0) > 0

    # Regression Run
    async def create_regression_run(self, regression: RegressionRun) -> RegressionRun:
        self.db.add(regression)
        await self.db.flush()
        return regression

    async def get_regression_runs(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[RegressionRun]:
        stmt = (
            select(RegressionRun)
            .where(RegressionRun.project_id == project_id)
            .order_by(desc(RegressionRun.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # Prompt Version
    async def create_prompt_version(self, prompt: PromptVersion) -> PromptVersion:
        self.db.add(prompt)
        await self.db.flush()
        return prompt

    async def get_prompt_versions(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[PromptVersion]:
        stmt = (
            select(PromptVersion)
            .where(PromptVersion.project_id == project_id)
            .order_by(desc(PromptVersion.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # Risk Assessment
    async def create_risk_assessment(
        self, assessment: RiskAssessment
    ) -> RiskAssessment:
        self.db.add(assessment)
        await self.db.flush()
        return assessment

    async def get_risk_assessments(
        self, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[RiskAssessment]:
        stmt = (
            select(RiskAssessment)
            .where(RiskAssessment.project_id == project_id)
            .order_by(desc(RiskAssessment.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
