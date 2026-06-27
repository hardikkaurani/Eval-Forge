from app.evaluation.judges.base import BaseJudge, JudgeResult
from app.evaluation.registry.registry import judge_registry
from app.evaluation.rubrics.rubrics import Rubric
from app.evaluation.prompts.engine import prompt_engine
from app.evaluation.utils.helpers import parse_json_from_text

@judge_registry.register("rubric")
class RubricJudge(BaseJudge):
    """Judge that scores model output against a single rubric in a single pass."""

    async def evaluate(
        self,
        prompt: str,
        output: str,
        reference: str | None = None,
        rubric: Rubric | None = None,
        **kwargs
    ) -> JudgeResult:
        if not rubric:
            raise ValueError("Rubric must be provided for RubricJudge.")

        system_prompt = prompt_engine.render("system")
        judge_prompt = prompt_engine.render(
            "rubric_scoring",
            prompt=prompt,
            output=output,
            reference=reference,
            rubric=rubric
        )

        response = await self.provider.generate(
            prompt=judge_prompt,
            system_prompt=system_prompt,
            **kwargs
        )

        try:
            parsed = parse_json_from_text(response.text)
            score = float(parsed.get("score", 0.0))
            confidence = float(parsed.get("confidence", 1.0))
            reasoning = parsed.get("reasoning", "")
        except Exception as e:
            score = 0.0
            confidence = 0.0
            reasoning = f"Failed to parse response: {str(e)}. Raw text: {response.text}"

        return JudgeResult(
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            metadata={
                "model_name": response.model_name,
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "latency_ms": response.latency_ms
            }
        )
