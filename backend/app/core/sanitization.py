import html
import re
from typing import Any, Dict, List, Union

DANGEROUS_SCHEMES_PATTERN = re.compile(
    r"^\s*(javascript|vbscript|data)\s*:", re.IGNORECASE
)


def sanitize_xss(text: str) -> str:
    """Escapes user metadata strings (names, descriptions, titles) using HTML entity encoding to prevent XSS execution.

    Leaves evaluation prompts, LLM model responses, code snippets, and benchmark data completely untouched.
    """
    if not text or not isinstance(text, str):
        return text

    return html.escape(text.strip(), quote=True)


def sanitize_url(url: str) -> str:
    """Neutralizes dangerous pseudo-protocol URI schemes (javascript:, vbscript:, data:text/html) on URL/source metadata fields.

    Preserves valid http://, https://, and relative paths /...
    """
    if not url or not isinstance(url, str):
        return url

    cleaned = url.strip()
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", cleaned)

    if DANGEROUS_SCHEMES_PATTERN.match(cleaned):
        return ""

    return html.escape(cleaned, quote=True)


def sanitize_input_data(
    data: Union[Dict[str, Any], List[Any], str],
    target_fields: tuple[str, ...] = ("name", "description", "title", "owner"),
    url_fields: tuple[str, ...] = ("source", "url", "website", "link"),
) -> Union[Dict[str, Any], List[Any], str]:
    """Recursively sanitizes specified UI-rendered string fields and URL fields in a payload.

    Leaves evaluation prompts, dataset records, and code fields intact.
    """
    if isinstance(data, str):
        return sanitize_xss(data)

    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if key in target_fields and isinstance(value, str):
                sanitized[key] = sanitize_xss(value)
            elif key in url_fields and isinstance(value, str):
                sanitized[key] = sanitize_url(value)
            elif isinstance(value, (dict, list)):
                sanitized[key] = sanitize_input_data(value, target_fields, url_fields)
            else:
                sanitized[key] = value
        return sanitized

    if isinstance(data, list):
        return [sanitize_input_data(item, target_fields, url_fields) for item in data]

    return data




