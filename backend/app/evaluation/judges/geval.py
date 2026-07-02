from app.evaluation.judges.base import BaseJudge, JudgeResult
from app.evaluation.prompts.engine import prompt_engine
from app.evaluation.registry.registry import judge_registry
from app.evaluation.rubrics.rubrics import Rubric
from app.evaluation.utils.helpers import parse_json_from_text


@judge_registry.register("geval")
class GEvalJudge(BaseJudge):
    """Judge that implements the two-pass G-Eval evaluation pipeline."""

    display_name = "G-Eval"

    async def evaluate(
        self,
        prompt: str,
        output: str,
        reference: str | None = None,
        rubric: Rubric | None = None,
        **kwargs,
    ) -> JudgeResult:
        if not rubric:
            raise ValueError("Rubric must be provided for GEvalJudge.")

        # Step 1: Generate evaluation steps
        system_prompt = prompt_engine.render("system")
        step_gen_prompt = prompt_engine.render("geval_step_gen", rubric=rubric)

        step_response = await self.provider.generate(
            prompt=step_gen_prompt, system_prompt=system_prompt, **kwargs
        )

        try:
            steps = parse_json_from_text(step_response.text)
            if not isinstance(steps, list):
                raise ValueError("Steps output must be a list.")
        except Exception:
            # If step generation fails, fall back to default rubric prompt
            steps = [
                f"Directly evaluate output based on description: {rubric.description}"
            ]

        # Step 2: Score output using steps
        scoring_prompt = prompt_engine.render(
            "geval_scoring",
            rubric=rubric,
            steps=steps,
            prompt=prompt,
            output=output,
            reference=reference,
        )

        score_response = await self.provider.generate(
            prompt=scoring_prompt, system_prompt=system_prompt, **kwargs
        )

        try:
            parsed = parse_json_from_text(score_response.text)
            score = float(parsed.get("score", 0.0))
            confidence = float(parsed.get("confidence", 1.0))
            reasoning = parsed.get("reasoning", "")
            criterion_scores = parsed.get("criterion_scores", {})
        except Exception as e:
            score = 0.0
            confidence = 0.0
            reasoning = f"Failed to parse G-Eval scoring response: {str(e)}. Raw text: {score_response.text}"
            criterion_scores = {}

        # Add total execution tokens and latency metrics
        prompt_tokens = (step_response.prompt_tokens or 0) + (
            score_response.prompt_tokens or 0
        )
        completion_tokens = (step_response.completion_tokens or 0) + (
            score_response.completion_tokens or 0
        )
        latency_ms = (step_response.latency_ms or 0) + (score_response.latency_ms or 0)

        return JudgeResult(
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            criterion_scores=criterion_scores,
            metadata={
                "steps": steps,
                "model_name": score_response.model_name,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "latency_ms": latency_ms,
                "raw_response": score_response.text,
            },
        )
