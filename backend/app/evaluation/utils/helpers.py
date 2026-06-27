import json
import re


def parse_json_from_text(text: str) -> any:
    """Extracts and parses JSON object or list from a string that might contain markdown fences."""
    cleaned = text.strip()

    # Try direct parsing
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try matching within markdown codeblocks
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try matching first '{' and last '}'
    start_brace = cleaned.find("{")
    end_brace = cleaned.rfind("}")
    if start_brace != -1 and end_brace != -1:
        try:
            return json.loads(cleaned[start_brace:end_brace+1])
        except json.JSONDecodeError:
            pass

    # Try matching first '[' and last ']'
    start_bracket = cleaned.find("[")
    end_bracket = cleaned.rfind("]")
    if start_bracket != -1 and end_bracket != -1:
        try:
            return json.loads(cleaned[start_bracket:end_bracket+1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Failed to extract valid JSON from text: {text[:200]}...")
