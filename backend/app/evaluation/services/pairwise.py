import math
from typing import Dict

from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation import ModelEloRating
from app.utils.time import get_utc_now
from app.utils.uuid import generate_uuid


class PairwiseComparisonResult(BaseModel):
    project_id: str
    model_a: str
    model_b: str
    winner: str  # "A", "B", or "Tie"
    score_a: float
    score_b: float
    old_elo_a: float
    old_elo_b: float
    new_elo_a: float
    new_elo_b: float
    elo_delta_a: float
    elo_delta_b: float
    confidence: float
    reasoning: str


def calculate_elo(
    rating_a: float, rating_b: float, winner: str, k_factor: float = 32.0
) -> tuple[float, float, float, float]:
    """Calculates updated ELO ratings and rating deltas for Model A and Model B.

    Formula:
      Expected A = 1 / (1 + 10^((Rating_B - Rating_A) / 400))
      Score A    = 1.0 if A wins, 0.0 if B wins, 0.5 if Tie
      New Rating = Old Rating + K * (Score - Expected)
    """
    expected_a = 1.0 / (1.0 + math.pow(10.0, (rating_b - rating_a) / 400.0))
    expected_b = 1.0 - expected_a

    if winner.upper() == "A":
        score_a, score_b = 1.0, 0.0
    elif winner.upper() == "B":
        score_a, score_b = 0.0, 1.0
    else:
        score_a, score_b = 0.5, 0.5

    delta_a = k_factor * (score_a - expected_a)
    delta_b = k_factor * (score_b - expected_b)

    new_rating_a = rating_a + delta_a
    new_rating_b = rating_b + delta_b

    return (
        round(new_rating_a, 2),
        round(new_rating_b, 2),
        round(delta_a, 2),
        round(delta_b, 2),
    )


class PairwiseService:
    @staticmethod
    async def get_elo_ratings(db: AsyncSession, project_id: str) -> Dict[str, float]:
        """Fetch current ELO ratings map for models in a project from the database."""
        stmt = (
            select(ModelEloRating)
            .where(ModelEloRating.project_id == project_id)
            .order_by(desc(ModelEloRating.rating))
        )
        res = await db.execute(stmt)
        records = res.scalars().all()

        if not records:
            # Default seed models if none exist yet for project
            return {
                "gpt-4o": 1500.0,
                "gemini-1.5-pro": 1485.0,
                "claude-3-5-sonnet": 1520.0,
                "llama-3-70b": 1440.0,
            }

        return {r.model_name: r.rating for r in records}

    @staticmethod
    async def record_pairwise_outcome(
        db: AsyncSession,
        project_id: str,
        model_a: str,
        model_b: str,
        winner: str,
        reasoning: str = "",
        confidence: float = 1.0,
        k_factor: float = 32.0,
    ) -> PairwiseComparisonResult:
        """Records outcome of A vs B comparison and updates ELO ratings transactionally in DB."""
        # 1. Fetch rating record for Model A
        stmt_a = select(ModelEloRating).where(
            ModelEloRating.project_id == project_id,
            ModelEloRating.model_name == model_a,
        )
        res_a = await db.execute(stmt_a)
        record_a = res_a.scalar_one_or_none()
        if not record_a:
            record_a = ModelEloRating(
                id=generate_uuid(),
                project_id=project_id,
                model_name=model_a,
                rating=1500.0,
                matches_played=0,
                wins=0,
                losses=0,
                draws=0,
                updated_at=get_utc_now(),
            )
            db.add(record_a)

        # 2. Fetch rating record for Model B
        stmt_b = select(ModelEloRating).where(
            ModelEloRating.project_id == project_id,
            ModelEloRating.model_name == model_b,
        )
        res_b = await db.execute(stmt_b)
        record_b = res_b.scalar_one_or_none()
        if not record_b:
            record_b = ModelEloRating(
                id=generate_uuid(),
                project_id=project_id,
                model_name=model_b,
                rating=1500.0,
                matches_played=0,
                wins=0,
                losses=0,
                draws=0,
                updated_at=get_utc_now(),
            )
            db.add(record_b)

        old_a = record_a.rating
        old_b = record_b.rating

        new_a, new_b, delta_a, delta_b = calculate_elo(
            old_a, old_b, winner, k_factor=k_factor
        )

        record_a.rating = new_a
        record_a.matches_played += 1
        if winner.upper() == "A":
            record_a.wins += 1
        elif winner.upper() == "B":
            record_a.losses += 1
        else:
            record_a.draws += 1
        record_a.updated_at = get_utc_now()

        record_b.rating = new_b
        record_b.matches_played += 1
        if winner.upper() == "B":
            record_b.wins += 1
        elif winner.upper() == "A":
            record_b.losses += 1
        else:
            record_b.draws += 1
        record_b.updated_at = get_utc_now()

        await db.commit()
        await db.refresh(record_a)
        await db.refresh(record_b)

        score_a = (
            1.0 if winner.upper() == "A" else (0.5 if winner.upper() == "TIE" else 0.0)
        )
        score_b = 1.0 - score_a

        return PairwiseComparisonResult(
            project_id=project_id,
            model_a=model_a,
            model_b=model_b,
            winner=winner,
            score_a=score_a,
            score_b=score_b,
            old_elo_a=old_a,
            old_elo_b=old_b,
            new_elo_a=new_a,
            new_elo_b=new_b,
            elo_delta_a=delta_a,
            elo_delta_b=delta_b,
            confidence=confidence,
            reasoning=reasoning
            or f"Pairwise evaluation completed with winner '{winner}'.",
        )
