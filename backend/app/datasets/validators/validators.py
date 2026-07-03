from typing import Any, Dict, List, Tuple
from app.datasets.exceptions.exceptions import DatasetValidationException


class DatasetValidator:
    """Validator class to verify structure, data integrity, and rules of evaluation datasets."""

    @staticmethod
    def validate_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validates a list of raw records (dicts), checking constraints.

        Returns a validation report.
        """
        report = {
            "valid": True,
            "total_records": len(records),
            "valid_records_count": 0,
            "invalid_records_count": 0,
            "errors": [],
            "warnings": [],
        }

        if not records:
            report["valid"] = False
            report["errors"].append({"row": 0, "message": "Dataset contains zero records."})
            return report

        prompts_seen = set()

        for idx, row in enumerate(records):
            row_num = idx + 1
            row_errors = []

            # 1. Prompt is mandatory
            prompt = row.get("prompt")
            if prompt is None or str(prompt).strip() == "":
                row_errors.append(f"Row {row_num}: 'prompt' is a required non-empty field.")

            # 2. Check types of common fields
            for field in ["input", "context", "reference_output", "candidate_output", "ground_truth"]:
                val = row.get(field)
                if val is not None and not isinstance(val, str):
                    row_errors.append(f"Row {row_num}: Field '{field}' must be a string.")

            # 3. Check expected_score is float
            expected_score = row.get("expected_score")
            if expected_score is not None:
                try:
                    float(expected_score)
                except (ValueError, TypeError):
                    row_errors.append(f"Row {row_num}: 'expected_score' must be a numeric value.")

            # 4. Check for duplicate prompts
            if prompt:
                p_str = str(prompt).strip()
                if p_str in prompts_seen:
                    report["warnings"].append(
                        {"row": row_num, "message": f"Duplicate prompt detected: '{p_str[:50]}...'"}
                    )
                else:
                    prompts_seen.add(p_str)

            # 5. Check integrity (e.g. if we have reference, do we have ground truth etc., just warnings)
            if not row.get("reference_output") and not row.get("ground_truth"):
                report["warnings"].append(
                    {
                        "row": row_num,
                        "message": "Both 'reference_output' and 'ground_truth' are empty. Reference-based evaluations might fail.",
                    }
                )

            # Accumulate errors
            if row_errors:
                report["invalid_records_count"] += 1
                for err in row_errors:
                    report["errors"].append({"row": row_num, "message": err})
            else:
                report["valid_records_count"] += 1

        if report["invalid_records_count"] > 0:
            report["valid"] = False

        return report

    @staticmethod
    def validate_file_content(content: bytes) -> Tuple[bool, str | None]:
        """Validates that file content can be decoded (UTF-8)."""
        try:
            content.decode("utf-8")
            return True, None
        except UnicodeDecodeError as e:
            return False, f"File encoding is not valid UTF-8: {str(e)}"
