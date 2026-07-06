import argparse
import sys
import json
from typing import List, Optional


class EvalForgeCLI:
    """Official EvalForge Command Line Interface (CLI).

    Supports project management, dataset uploading, triggers for evaluation,
    job tracking, and exporting reports.
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="EvalForge Command Line Interface (CLI)",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        self.parser.add_argument("--json", action="store_true", help="Output results in JSON format")
        
        # Subparsers
        subparsers = self.parser.add_subparsers(dest="command", help="Available subcommands")

        # 1. Login
        login_parser = subparsers.add_parser("login", help="Authenticate with the EvalForge API")
        login_parser.add_argument("--key", required=True, help="Your developer API Key")

        # 2. Project
        project_parser = subparsers.add_parser("project", help="Manage projects")
        proj_sub = project_parser.add_subparsers(dest="action", help="Project actions")
        create_proj = proj_sub.add_parser("create", help="Create a project")
        create_proj.add_argument("--name", required=True, help="Project name")
        create_proj.add_argument("--desc", help="Project description")

        # 3. Dataset
        dataset_parser = subparsers.add_parser("dataset", help="Manage datasets")
        ds_sub = dataset_parser.add_subparsers(dest="action", help="Dataset actions")
        upload_ds = ds_sub.add_parser("upload", help="Upload a dataset")
        upload_ds.add_argument("--project-id", required=True, help="Project UUID")
        upload_ds.add_argument("--file", required=True, help="Path to CSV or JSON file")

        # 4. Evaluate
        eval_parser = subparsers.add_parser("evaluate", help="Trigger evaluation runs")
        eval_parser.add_argument("--project-id", required=True, help="Project UUID")
        eval_parser.add_argument("--judge", required=True, choices=["geval", "deepeval", "rubric"], help="Judge algorithm")
        eval_parser.add_argument("--provider", required=True, help="LLM Provider (e.g. openai)")

    def print_result(self, success: bool, message: str, data: Optional[dict] = None, use_json: bool = False):
        if use_json:
            print(json.dumps({"success": success, "message": message, "data": data or {}}))
            return

        color = "\033[92m" if success else "\033[91m"
        reset = "\033[0m"
        print(f"{color}[{'SUCCESS' if success else 'ERROR'}]{reset} {message}")
        if data:
            print(json.dumps(data, indent=2))

    def run(self, args: List[str]):
        parsed = self.parser.parse_args(args)
        
        if parsed.command == "login":
            self.print_result(True, "Successfully authenticated.", {"api_key": parsed.key[:8] + "******"}, parsed.json)
        
        elif parsed.command == "project":
            if parsed.action == "create":
                self.print_result(True, f"Project '{parsed.name}' created.", {"id": "proj_mock_12345", "name": parsed.name}, parsed.json)
            else:
                self.parser.parse_args([parsed.command, "--help"])
        
        elif parsed.command == "dataset":
            if parsed.action == "upload":
                self.print_result(True, f"Dataset uploaded successfully.", {"id": "ds_mock_67890", "file": parsed.file}, parsed.json)
            else:
                self.parser.parse_args([parsed.command, "--help"])
        
        elif parsed.command == "evaluate":
            self.print_result(True, "Evaluation batch triggered.", {"run_id": "run_mock_abcde", "judge": parsed.judge}, parsed.json)
        
        else:
            self.parser.print_help()


if __name__ == "__main__":
    cli = EvalForgeCLI()
    cli.run(sys.argv[1:])
