import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.datasets.exceptions.exceptions import ExperimentNotFoundException
from app.datasets.repositories.dataset import DatasetRepository
from app.datasets.repositories.experiment import ExperimentRepository
from app.evaluation.pipelines.pipeline import EvaluationPipeline
from app.evaluation.schemas.evaluation import BatchEvaluationRequest, TestCaseInput
from app.models.dataset import Experiment
from app.models.evaluation import EvaluationResult
from app.utils.time import get_utc_now

logger = logging.getLogger(__name__)


class ExperimentService:
    """Service to manage evaluation Experiments, running pipelines over datasets and tracking results."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.experiment_repo = ExperimentRepository(db)
        self.dataset_repo = DatasetRepository(db)

    async def create_experiment(
        self,
        project_id: str,
        dataset_version_id: str,
        name: str,
        description: Optional[str] = None,
        judge: str = "rubric",
        provider: str = "openai",
        model: Optional[str] = None,
        configuration: Dict[str, Any] = None,
    ) -> Experiment:
        configuration = configuration or {
            "temperature": 0.0,
            "max_tokens": None,
            "threshold": 0.7,
            "timeout": 30.0,
            "retry_count": 2,
        }

        # Check that version exists
        version = await self.dataset_repo.get_version(dataset_version_id)
        if not version:
            raise ValueError(f"Dataset version '{dataset_version_id}' not found.")

        experiment = await self.experiment_repo.create_experiment(
            project_id=project_id,
            dataset_version_id=dataset_version_id,
            name=name,
            description=description,
            judge=judge,
            provider=provider,
            model=model,
            configuration=configuration,
        )
        await self.db.commit()
        return experiment

    async def get_experiment(self, experiment_id: str) -> Experiment:
        experiment = await self.experiment_repo.get_experiment(experiment_id)
        if not experiment:
            raise ExperimentNotFoundException(experiment_id)
        return experiment

    async def list_experiments(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[Experiment], int]:
        return await self.experiment_repo.list_experiments(
            project_id=project_id,
            skip=skip,
            limit=limit,
            search=search,
            status=status,
        )

    async def delete_experiment(self, experiment_id: str) -> None:
        success = await self.experiment_repo.delete_experiment(experiment_id)
        if not success:
            raise ExperimentNotFoundException(experiment_id)
        await self.db.commit()

    async def execute_experiment(self, experiment_id: str) -> Experiment:
        """Executes the evaluation pipeline asynchronously for all dataset records."""
        experiment = await self.get_experiment(experiment_id)

        try:
            # 1. Update status to RUNNING
            experiment.status = "RUNNING"
            experiment.started_at = get_utc_now()
            await self.db.commit()

            # 2. Get dataset records
            records, _ = await self.dataset_repo.get_records(
                experiment.dataset_version_id, limit=1000000
            )
            if not records:
                raise ValueError(
                    "No records found in the associated dataset version to evaluate."
                )

            # 3. Map records to TestCaseInput schemas
            test_cases = []
            for rec in records:
                # Ensure we fall back if reference/ground truth/candidate output not present
                test_cases.append(
                    TestCaseInput(
                        input_prompt=rec.prompt,
                        model_output=rec.candidate_output or rec.expected_score or "",
                        reference=rec.reference_output or rec.ground_truth or "",
                        response_b=rec.custom_fields.get("response_b"),  # for pairwise
                    )
                )

            # 4. Construct BatchEvaluationRequest
            request = BatchEvaluationRequest(
                project_id=experiment.project_id,
                evaluation_name=experiment.name,
                evaluation_description=experiment.description,
                judge=experiment.judge,
                provider=experiment.provider,
                provider_model=experiment.model,
                test_cases=test_cases,
                configuration=experiment.configuration,
            )

            # 5. Run evaluation pipeline
            # This calls judges, invokes LLMs, inserts evaluation run/results database records
            eval_run = await EvaluationPipeline.run(self.db, request)

            # 6. Fetch results to populate experiment details
            results_query = (
                select(EvaluationResult)
                .where(EvaluationResult.run_id == eval_run.id)
                .options(
                    selectinload(EvaluationResult.rubric_scores),
                    selectinload(EvaluationResult.provider_metadata),
                )
            )
            results_result = await self.db.execute(results_query)
            eval_results = results_result.scalars().all()

            # 7. Aggregate stats and construct results JSON
            results_json = []
            for r in eval_results:
                results_json.append(
                    {
                        "id": r.id,
                        "prompt": r.input_prompt,
                        "output": r.model_output,
                        "reference": r.reference,
                        "score": r.score,
                        "passed": r.passed,
                        "reasoning": r.reasoning,
                        "evaluated_at": r.evaluated_at.isoformat()
                        if r.evaluated_at
                        else None,
                    }
                )

            # Update Experiment metrics and state
            completed_time = get_utc_now()
            duration = (completed_time - experiment.started_at).total_seconds()

            experiment.status = "COMPLETED"
            experiment.completed_at = completed_time
            experiment.duration_seconds = duration
            experiment.metrics = {
                "total_cases": len(eval_results),
                "completed_cases": len(eval_results),
                "failed_cases": 0,
                "success_rate": eval_run.success_rate or 1.0,
                "aggregate_score": eval_run.aggregate_score or 0.0,
            }
            experiment.results = results_json

            await self.db.commit()
            return experiment

        except Exception as e:
            logger.exception("Experiment execution failed")
            experiment.status = "FAILED"
            experiment.completed_at = get_utc_now()
            experiment.metrics = {"error": str(e)}
            await self.db.commit()
            raise e
