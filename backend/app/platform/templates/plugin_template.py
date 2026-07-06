"""EvalForge Plugin Template.

Inherit from this base layout to implement custom LLM judges, metrics, or exporters
and load them using the plugin engine registry.
"""

from typing import Any, Dict


class BasePlugin:
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Plugins must override the execute method.")


class CustomMetricPlugin(BasePlugin):
    """Example implementation of a custom metric evaluation plugin."""

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Extract inputs
        inputs.get("prompt", "")
        output = inputs.get("output", "")
        reference = inputs.get("reference", "")

        # Perform metric calculation logic
        score = 1.0 if reference in output else 0.5

        return {
            "success": True,
            "metric_score": score * self.settings.get("scale_factor", 1.0),
            "reasoning": "Evaluated match criteria successfully.",
        }
