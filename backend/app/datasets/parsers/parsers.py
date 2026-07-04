import csv
import io
import json
from typing import Any, Dict, List

from app.datasets.exceptions.exceptions import InvalidDatasetFormatException


class DatasetParser:
    """Core parser orchestrator to convert multiple file formats into structured lists of dictionaries."""

    @staticmethod
    def parse(file_content: bytes, file_format: str) -> List[Dict[str, Any]]:
        """Dispatches file content to the appropriate parser based on the file format string."""
        fmt = file_format.lower().strip()

        if fmt == "csv":
            return DatasetParser.parse_csv(file_content)
        elif fmt == "json":
            return DatasetParser.parse_json(file_content)
        elif fmt == "jsonl":
            return DatasetParser.parse_jsonl(file_content)
        elif fmt in ["xlsx", "xls", "excel"]:
            return DatasetParser.parse_excel(file_content)
        elif fmt == "parquet":
            return DatasetParser.parse_parquet(file_content)
        else:
            raise InvalidDatasetFormatException(
                file_format, "No parser registered for this format."
            )

    @staticmethod
    def parse_csv(content: bytes) -> List[Dict[str, Any]]:
        """Parses CSV bytes using standard library."""
        try:
            text = content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text))
            records = []
            for row in reader:
                # Convert tags string (if present as comma separated) to list
                if (
                    "tags" in row
                    and isinstance(row["tags"], str)
                    and row["tags"].strip()
                ):
                    row["tags"] = [
                        t.strip() for t in row["tags"].split(",") if t.strip()
                    ]
                elif "tags" not in row:
                    row["tags"] = []

                # Convert expected_score to float if possible
                if "expected_score" in row and row["expected_score"]:
                    try:
                        row["expected_score"] = float(row["expected_score"])
                    except ValueError:
                        pass

                # Parse custom_fields and metadata_json if they exist as serialized json
                for json_field in ["custom_fields", "metadata_json"]:
                    if (
                        json_field in row
                        and isinstance(row[json_field], str)
                        and row[json_field].strip()
                    ):
                        try:
                            row[json_field] = json.loads(row[json_field])
                        except json.JSONDecodeError:
                            pass

                records.append(dict(row))
            return records
        except Exception as e:
            raise InvalidDatasetFormatException(
                "csv", f"CSV parsing failed: {str(e)}"
            ) from e

    @staticmethod
    def parse_json(content: bytes) -> List[Dict[str, Any]]:
        """Parses JSON bytes. Expects either a list of dicts, or a dict containing a 'records' list."""
        try:
            data = json.loads(content.decode("utf-8"))
            if isinstance(data, list):
                records = data
            elif (
                isinstance(data, dict)
                and "records" in data
                and isinstance(data["records"], list)
            ):
                records = data["records"]
            else:
                raise ValueError(
                    "JSON must be a list of records or an object containing a 'records' key list."
                )

            # Validate type of each record
            for r in records:
                if not isinstance(r, dict):
                    raise ValueError(
                        "Each record in the JSON dataset must be an object."
                    )
            return records
        except Exception as e:
            raise InvalidDatasetFormatException(
                "json", f"JSON parsing failed: {str(e)}"
            ) from e

    @staticmethod
    def parse_jsonl(content: bytes) -> List[Dict[str, Any]]:
        """Parses JSONL bytes line by line."""
        try:
            lines = content.decode("utf-8").splitlines()
            records = []
            for idx, line in enumerate(lines):
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    record = json.loads(line_str)
                    if not isinstance(record, dict):
                        raise ValueError(f"Line {idx + 1} is not a valid JSON object.")
                    records.append(record)
                except json.JSONDecodeError as je:
                    raise ValueError(
                        f"Line {idx + 1} is invalid JSON: {str(je)}"
                    ) from je
            return records
        except Exception as e:
            raise InvalidDatasetFormatException(
                "jsonl", f"JSONL parsing failed: {str(e)}"
            ) from e

    @staticmethod
    def parse_excel(content: bytes) -> List[Dict[str, Any]]:
        """Parses Excel bytes using Pandas and openpyxl if installed."""
        try:
            import pandas as pd
        except ImportError as e:
            raise InvalidDatasetFormatException(
                "excel",
                "The 'pandas' and 'openpyxl' libraries are required to parse Excel files.",
            ) from e

        try:
            df = pd.read_excel(io.BytesIO(content))
            # replace NaN with None for json compatibility
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
        except Exception as e:
            raise InvalidDatasetFormatException(
                "excel", f"Excel parsing failed: {str(e)}"
            ) from e

    @staticmethod
    def parse_parquet(content: bytes) -> List[Dict[str, Any]]:
        """Parses Parquet bytes using Pandas and pyarrow if installed."""
        try:
            import pandas as pd
        except ImportError as e:
            raise InvalidDatasetFormatException(
                "parquet",
                "The 'pandas' and 'pyarrow' libraries are required to parse Parquet files.",
            ) from e

        try:
            df = pd.read_parquet(io.BytesIO(content))
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
        except Exception as e:
            raise InvalidDatasetFormatException(
                "parquet", f"Parquet parsing failed: {str(e)}"
            ) from e

    @staticmethod
    def parse_huggingface(repo_id: str, split: str = "train") -> List[Dict[str, Any]]:
        """Downloads and parses a dataset from HuggingFace Hub if 'datasets' library is installed."""
        try:
            from datasets import load_dataset
        except ImportError as e:
            raise InvalidDatasetFormatException(
                "huggingface",
                "The 'datasets' library is required to import from HuggingFace.",
            ) from e

        try:
            dataset = load_dataset(repo_id, split=split)
            records = []
            for row in dataset:
                records.append(dict(row))
            return records
        except Exception as e:
            raise InvalidDatasetFormatException(
                "huggingface", f"HuggingFace download/parsing failed: {str(e)}"
            ) from e
