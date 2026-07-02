from dataclasses import dataclass
from typing import Any

from jinja2 import Template


@dataclass(frozen=True, slots=True)
class PromptTemplateVersion:
    name: str
    version: str
    template: str
    description: str | None = None

DEFAULT_SYSTEM_PROMPT = (
    "You are an expert AI evaluator. Your job is to strictly evaluate the quality of LLM outputs "
    "according to specified rubrics, metrics, and ground truth references.\n"
    "You must return your output in structured JSON format with no additional conversational text.\n"
    "Ensure your evaluation is objective, rigorous, and logically consistent."
)

DEFAULT_RUBRIC_SCORING_PROMPT = (
    "Evaluate the following LLM output based on the prompt, reference context (if any), and rubric criteria.\n\n"
    "### Evaluation Criteria:\n"
    "Rubric Name: {{ rubric.name }}\n"
    "Description: {{ rubric.description }}\n"
    "Scoring Scale: 1 to {{ rubric.scoring_scale }}\n\n"
    "### Inputs:\n"
    "User Prompt: {{ prompt }}\n"
    "Model Output: {{ output }}\n"
    "{% if reference %}Reference Context/Ground Truth: {{ reference }}\n{% endif %}\n"
    "### Evaluation Instructions:\n"
    "{{ rubric.prompt_template }}\n\n"
    "Provide a numeric score (float), a confidence level between 0.0 and 1.0, and detailed reasoning.\n"
    "Your output MUST be a JSON object matching this structure:\n"
    "{\n"
    '  "score": <float>,\n'
    '  "confidence": <float>,\n'
    '  "reasoning": "<string>"\n'
    "}"
)

DEFAULT_GEVAL_STEP_GEN_PROMPT = (
    "You are an expert system designer. Given the following evaluation rubric, write an ordered list of "
    "concrete, step-by-step instructions to guide an evaluator in scoring a response.\n\n"
    "### Rubric Criteria:\n"
    "Name: {{ rubric.name }}\n"
    "Description: {{ rubric.description }}\n"
    "Scoring Scale: 1 to {{ rubric.scoring_scale }}\n\n"
    "Generate 3 to 5 clear, sequentially ordered evaluation steps. Do not score anything yet.\n"
    "Your output MUST be a JSON list of strings, like this:\n"
    "[\n"
    '  "Step 1: Check if...",\n'
    '  "Step 2: Verify that..."\n'
    "]"
)

DEFAULT_GEVAL_SCORING_PROMPT = (
    "You are an expert evaluator. Score the model output on a scale of 1 to {{ rubric.scoring_scale }} "
    "by strictly following the evaluation steps below.\n\n"
    "### Rubric:\n"
    "Name: {{ rubric.name }}\n"
    "Description: {{ rubric.description }}\n\n"
    "### Evaluation Steps:\n"
    "{% for step in steps %}"
    "{{ loop.index }}. {{ step }}\n"
    "{% endfor %}\n"
    "### Inputs:\n"
    "User Prompt: {{ prompt }}\n"
    "Model Output: {{ output }}\n"
    "{% if reference %}Reference Context/Ground Truth: {{ reference }}\n{% endif %}\n"
    "### Instructions:\n"
    "Provide a detailed score (float) between 1.0 and {{ rubric.scoring_scale }}. Evaluate how well the model "
    "adheres to each evaluation step in your reasoning.\n\n"
    "Your output MUST be a JSON object matching this structure:\n"
    "{\n"
    '  "score": <float>,\n'
    '  "confidence": <float>,\n'
    '  "reasoning": "<string>",\n'
    '  "criterion_scores": {\n'
    '     "step_scores": [\n'
    "        {% for step in steps %}"
    '        {"step": "{{ step }}", "score": <float>}{% if not loop.last %},{% endif %}\n'
    "        {% endfor %}"
    "     ]\n"
    "  }\n"
    "}"
)

DEFAULT_PAIRWISE_PROMPT = (
    "You are an impartial judge. Compare the quality of the two model responses (Response A and Response B) "
    "to the user prompt.\n\n"
    "### User Prompt:\n"
    "{{ prompt }}\n\n"
    "### Response A:\n"
    "{{ response_a }}\n\n"
    "### Response B:\n"
    "{{ response_b }}\n\n"
    "{% if reference %}### Reference Context/Ground Truth:\n{{ reference }}\n\n{% endif %}"
    "### Instructions:\n"
    "1. Choose which response is better ('A' or 'B'), or declare a 'Tie'.\n"
    "2. Provide your confidence score between 0.0 and 1.0.\n"
    "3. Provide the score difference (on a 1 to 5 scale, where 0 means Tie and 5 means one response completely dominates the other).\n"
    "4. Detail your reasoning.\n\n"
    "Your output MUST be a JSON object matching this structure:\n"
    "{\n"
    '  "winner": "A" | "B" | "Tie",\n'
    '  "score_difference": <float>,\n'
    '  "confidence": <float>,\n'
    '  "reasoning": "<string>"\n'
    "}"
)


class PromptEngine:
    """Prompt template engine utilizing Jinja2 for dynamic compilation."""

    def __init__(self):
        self._templates: dict[str, dict[str, PromptTemplateVersion]] = {}
        self.register_template("system", DEFAULT_SYSTEM_PROMPT, version="v1")
        self.register_template(
            "rubric_scoring", DEFAULT_RUBRIC_SCORING_PROMPT, version="v1"
        )
        self.register_template(
            "geval_step_gen", DEFAULT_GEVAL_STEP_GEN_PROMPT, version="v1"
        )
        self.register_template(
            "geval_scoring", DEFAULT_GEVAL_SCORING_PROMPT, version="v1"
        )
        self.register_template("pairwise", DEFAULT_PAIRWISE_PROMPT, version="v1")

    def register_template(
        self,
        name: str,
        template_str: str,
        *,
        version: str = "v1",
        description: str | None = None,
    ) -> None:
        """Register or override a prompt template version."""
        self._templates.setdefault(name, {})[version] = PromptTemplateVersion(
            name=name, version=version, template=template_str, description=description
        )

    def get_versions(self, name: str) -> list[str]:
        return list(self._templates.get(name, {}).keys())

    def render(self, name: str, version: str = "v1", **context: Any) -> str:
        """Render a template version with a given context."""
        template_versions = self._templates.get(name)
        if not template_versions:
            raise KeyError(f"Prompt template '{name}' does not exist.")

        template_info = template_versions.get(version) or next(
            iter(template_versions.values())
        )
        template = Template(template_info.template)
        return template.render(**context)

    def describe(self, name: str) -> dict[str, Any]:
        versions = self._templates.get(name)
        if not versions:
            raise KeyError(f"Prompt template '{name}' does not exist.")
        return {
            "name": name,
            "versions": [
                {
                    "version": item.version,
                    "description": item.description,
                }
                for item in versions.values()
            ],
        }


prompt_engine = PromptEngine()
