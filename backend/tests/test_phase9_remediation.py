from unittest.mock import patch

import pytest
from jinja2.exceptions import SecurityError, UndefinedError

from app.analytics.services import ObservabilityService
from app.evaluation.prompts.engine import PromptEngine


def test_prompt_engine_jinja2_autoescape_and_ssti() -> None:
    """Verify PromptEngine renders XML tags without autoescaping, enforces StrictUndefined, and blocks SSTI."""
    engine = PromptEngine()

    # 1. Plain-text and XML tags MUST be preserved without HTML escaping
    template_str = "Prompt: {{ prompt }} | Output: <user_prompt>{{ user_data }}</user_prompt>"
    engine.register_template("test_xml", template_str, version="v1")

    rendered = engine.render("test_xml", version="v1", prompt="Analyze & test", user_data="<script>alert(1)</script>")
    # Notice _sanitize_value handles XML angle brackets safely while autoescape=False preserves raw template tags
    assert "<user_prompt>" in rendered
    assert "</user_prompt>" in rendered

    # 2. StrictUndefined must raise UndefinedError on missing variables
    engine.register_template("test_strict", "Hello {{ missing_var }}", version="v1")
    with pytest.raises(UndefinedError):
        engine.render("test_strict", version="v1")

    # 3. SSTI payloads must be blocked by SandboxedEnvironment
    engine.register_template("ssti_test", "{{ ''.__class__.__mro__ }}", version="v1")
    with pytest.raises(SecurityError):
        engine.render("ssti_test", version="v1")


@pytest.mark.asyncio
async def test_analytics_service_psutil_error_fallback(db_session) -> None:
    """Verify system stats collection logs warning and returns fallback zero metrics on psutil error."""
    service = ObservabilityService(db_session)

    with patch("psutil.cpu_percent", side_effect=RuntimeError("OS access error")):
        stats = await service.collect_health_metrics()
        assert stats["cpu_usage_percent"] == 0.0
        assert stats["memory_usage_bytes"] == 0
        assert stats["memory_usage_percent"] == 0.0
        assert stats["disk_usage_percent"] == 0.0

