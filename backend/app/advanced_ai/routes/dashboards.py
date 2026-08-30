from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.advanced_ai.services.policy_regression import PolicyRegressionService
from app.core.dependencies import _extract_workspace_id, get_current_api_key
from app.database.repository import ProjectRepository
from app.database.session import get_db
from app.models.advanced_ai import (
    Policy,
    RAGEvaluation,
    SafetyEvaluation,
    SecurityEvaluation,
)

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


async def _verify_project_ws(
    db: AsyncSession, project_id: str, workspace_id: str | None
) -> None:
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(project_id, workspace_id=workspace_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found.",
        )


@router.get("/summary", status_code=status.HTTP_200_OK)
async def get_advanced_ai_dashboard_summary(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Calculates overall metrics, readiness scores, and compiles security/safety/RAG dashboard views from DB."""
    workspace_id = _extract_workspace_id(current_key)
    await _verify_project_ws(db, project_id, workspace_id)

    # 1. Real Safety Score & Violations
    safety_res = await db.execute(
        select(
            func.coalesce(func.avg(SafetyEvaluation.safety_score), 100.0),
            func.count(SafetyEvaluation.id),
        ).where(SafetyEvaluation.project_id == project_id)
    )
    avg_safety, safety_count = safety_res.one()

    # 2. Real Security Score & Risk
    sec_res = await db.execute(
        select(
            func.coalesce(func.avg(SecurityEvaluation.risk_score), 0.0),
            func.count(SecurityEvaluation.id),
        ).where(SecurityEvaluation.project_id == project_id)
    )
    avg_sec_risk, sec_count = sec_res.one()
    security_score = max(0.0, 100.0 - float(avg_sec_risk or 0.0))

    # 3. Real RAG Metrics
    rag_res = await db.execute(
        select(
            func.coalesce(func.avg(RAGEvaluation.faithfulness), 0.0),
            func.coalesce(func.avg(RAGEvaluation.context_precision), 0.0),
            func.coalesce(func.avg(RAGEvaluation.context_recall), 0.0),
        ).where(RAGEvaluation.project_id == project_id)
    )
    avg_faith, avg_prec, avg_rec = rag_res.one()
    rag_score = (float(avg_faith) + float(avg_prec) + float(avg_rec)) / 3.0 * 100.0

    # 4. Active Policies
    policy_res = await db.execute(
        select(func.count(Policy.id)).where(
            Policy.project_id == project_id, Policy.is_active.is_(True)
        )
    )
    active_guardrails = policy_res.scalar_one()

    service = PolicyRegressionService(db)
    risk_assessment = await service.calculate_risk_assessment(
        project_id=project_id,
        entity_type="project_baseline",
        entity_id=project_id,
        security_score=security_score,
        safety_score=float(avg_safety),
    )

    overall_readiness = (security_score + float(avg_safety) + rag_score) / 3.0
    insights = service.generate_ai_insights(
        float(avg_safety), risk_assessment.overall_risk_score
    )

    return {
        "project_id": project_id,
        "overall_enterprise_readiness_score": round(overall_readiness, 2),
        "overall_risk_score": risk_assessment.overall_risk_score,
        "security_dashboard": {
            "score": round(security_score, 2),
            "evaluations_count": sec_count,
        },
        "safety_dashboard": {
            "score": round(float(avg_safety), 2),
            "evaluations_count": safety_count,
        },
        "rag_dashboard": {
            "score": round(rag_score, 2),
            "average_faithfulness": round(float(avg_faith), 4),
            "average_context_precision": round(float(avg_prec), 4),
            "average_context_recall": round(float(avg_rec), 4),
        },
        "policy_dashboard": {
            "active_guardrails": active_guardrails,
            "total_evaluations_count": safety_count + sec_count,
        },
        "ai_insights": insights,
    }
