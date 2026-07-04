import json
import pytest
from app.datasets.parsers.parsers import DatasetParser
from app.datasets.validators.validators import DatasetValidator
from app.datasets.exceptions.exceptions import DatasetValidationException, InvalidDatasetFormatException


def test_validator_with_valid_records():
    records = [
        {"prompt": "Translate 'hello'", "reference_output": "bonjour", "expected_score": 1.0},
        {"prompt": "Write a poem", "ground_truth": "Roses are red", "tags": ["creative"]},
    ]
    report = DatasetValidator.validate_records(records)
    assert report["valid"] is True
    assert report["total_records"] == 2
    assert report["valid_records_count"] == 2
    assert len(report["errors"]) == 0


def test_validator_with_invalid_records():
    # Empty prompt and invalid expected_score type
    records = [
        {"prompt": "  ", "reference_output": "bonjour"},
        {"prompt": "Write a poem", "expected_score": "not-a-float"},
    ]
    report = DatasetValidator.validate_records(records)
    assert report["valid"] is False
    assert report["invalid_records_count"] == 2
    assert len(report["errors"]) == 2


def test_parser_csv():
    csv_content = (
        "prompt,input,reference_output,expected_score,tags\n"
        "Explain quantum physics,System,Particles in wave,0.85,physics\n"
        "Solve 2+2,System,4,1.0,math\n"
    ).encode("utf-8")

    records = DatasetParser.parse(csv_content, "csv")
    assert len(records) == 2
    assert records[0]["prompt"] == "Explain quantum physics"
    assert records[0]["expected_score"] == 0.85
    assert records[0]["tags"] == ["physics"]
    assert records[1]["prompt"] == "Solve 2+2"
    assert records[1]["expected_score"] == 1.0
    assert records[1]["tags"] == ["math"]


def test_parser_json():
    json_data = [
        {"prompt": "Explain quantum physics", "expected_score": 0.85},
        {"prompt": "Solve 2+2", "expected_score": 1.0},
    ]
    json_content = json.dumps(json_data).encode("utf-8")
    records = DatasetParser.parse(json_content, "json")
    assert len(records) == 2
    assert records[0]["prompt"] == "Explain quantum physics"
    assert records[1]["prompt"] == "Solve 2+2"


def test_parser_jsonl():
    jsonl_content = (
        '{"prompt": "Explain quantum physics", "expected_score": 0.85}\n'
        '{"prompt": "Solve 2+2", "expected_score": 1.0}\n'
    ).encode("utf-8")
    records = DatasetParser.parse(jsonl_content, "jsonl")
    assert len(records) == 2
    assert records[0]["prompt"] == "Explain quantum physics"
    assert records[1]["prompt"] == "Solve 2+2"
