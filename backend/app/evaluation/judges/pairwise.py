from app.evaluation.judges.base import BaseJudge, JudgeResult
from app.evaluation.registry.registry import judge_registry
from app.evaluation.rubrics.rubrics import Rubric
from app.evaluation.prompts.engine import prompt_engine
from app.evaluation.utils.helpers import parse_json_from_text

@judge_registry.register("pairwise")
class PairwiseJudge(BaseJudge):
    """Judge that compares two model outputs side-by-side to select the winner."""

    async def evaluate(
        self,
        prompt: str,
        output: str,  # Treat this as response A
        reference: str | None = None,
        rubric: Rubric | None = None,
        **kwargs
    ) -> JudgeResult:
        # Pairwise requires response_b to compare against
        response_b = kwargs.get("response_b")
        if not response_b:
            raise ValueError("response_b must be provided for PairwiseJudge in kwargs.")

        system_prompt = prompt_engine.render("system")
        judge_prompt = prompt_engine.render(
            "pairwise",
            prompt=prompt,
            response_a=output,
            response_b=response_b,
            reference=reference
        )

        response = await self.provider.generate(
            prompt=judge_prompt,
            system_prompt=system_prompt,
            **kwargs
        )

        try:
            parsed = parse_json_from_text(response.text)
            winner = parsed.get("winner", "Tie").strip()
            score_diff = float(parsed.get("score_difference", 0.0))
            confidence = float(parsed.get("confidence", 1.0))
            reasoning = parsed.get("reasoning", "")
            
            # Map winner to a score
            # Winner A = 1.0, Tie = 0.5, Winner B = 0.0
            if winner == "A":
                score = 1.0
            elif winner == "B":
                score = 0.0
            else:
                score = 0.5
                winner = "Tie"
        except Exception as e:
            winner = "Tie"
            score = 0.5
            score_diff = 0.0
            confidence = 0.0
            reasoning = f"Failed to parse response: {str(e)}. Raw text: {response.text}"

        return JudgeResult(
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            winner=winner,
            metadata={
                "score_difference": score_diff,
                "model_name": response.model_name,
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "latency_ms": response.latency_ms
            }
        )
