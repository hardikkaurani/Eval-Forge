import hashlib
import json
from typing import Any, Dict, List


class DatasetMetadataEngine:
    """Automatic metadata extraction and dataset profiling engine."""

    @staticmethod
    def calculate_fingerprint(records: List[Dict[str, Any]]) -> str:
        """Generates a unique deterministic SHA-256 fingerprint for a list of records."""
        # Normalize and serialize records list deterministically
        serialized = json.dumps(records, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def profile_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Profiles the dataset records and computes metrics, stats, and scores."""
        total_records = len(records)
        if total_records == 0:
            return {
                "record_count": 0,
                "data_quality_score": 0.0,
                "avg_prompt_char_length": 0.0,
                "avg_prompt_word_length": 0.0,
                "duplicate_rate": 0.0,
                "missing_references_rate": 0.0,
            }

        prompt_chars = 0
        prompt_words = 0
        prompts = set()
        missing_references = 0
        tag_set = set()

        for row in records:
            # Stats on prompt
            prompt = str(row.get("prompt", ""))
            prompt_chars += len(prompt)
            prompt_words += len(prompt.split())

            # Duplicates
            prompts.add(prompt.strip())

            # Missing references
            if not row.get("reference_output") and not row.get("ground_truth"):
                missing_references += 1

            # Tags count
            tags = row.get("tags", [])
            if isinstance(tags, list):
                for t in tags:
                    tag_set.add(str(t).lower())

        # Calculations
        unique_prompts = len(prompts)
        duplicate_rate = (total_records - unique_prompts) / total_records if total_records > 0 else 0.0
        missing_references_rate = missing_references / total_records if total_records > 0 else 0.0

        # Quality scoring (starts at 100, drops on issues)
        quality_score = 100.0
        # Deduct for duplicates (e.g. up to 30 points)
        quality_score -= duplicate_rate * 30.0
        # Deduct for missing reference/ground truths (e.g. up to 40 points)
        quality_score -= missing_references_rate * 40.0
        # Deduct for extremely short prompts (less than 10 characters average)
        avg_char = prompt_chars / total_records
        if avg_char < 10.0:
            quality_score -= 15.0

        quality_score = max(0.0, round(quality_score, 2))

        return {
            "record_count": total_records,
            "data_quality_score": quality_score,
            "avg_prompt_char_length": round(prompt_chars / total_records, 2),
            "avg_prompt_word_length": round(prompt_words / total_records, 2),
            "duplicate_rate": round(duplicate_rate, 4),
            "missing_references_rate": round(missing_references_rate, 4),
            "unique_prompts_count": unique_prompts,
            "unique_tags": list(tag_set),
            "token_estimate": int((prompt_chars / 4) * 1.2),  # rough token estimate (1 token ~4 chars)
        }
