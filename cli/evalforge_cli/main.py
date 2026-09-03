import argparse
import json
import sys
from typing import Any, List, Optional

from evalforge_cli.client import CLIClient
from evalforge_cli.config import load_config, save_config


def print_output(data: Any, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(data, indent=2))
    elif isinstance(data, list):
        if not data:
            print("No items found.")
            return
        # Print table-like output
        keys = list(data[0].keys()) if isinstance(data[0], dict) else []
        if keys:
            header = " | ".join(k.upper() for k in keys[:5])
            print(header)
            print("-" * len(header))
            for item in data:
                print(" | ".join(str(item.get(k, "")) for k in keys[:5]))
        else:
            for item in data:
                print(str(item))
    elif isinstance(data, dict):
        for k, v in data.items():
            print(f"{k}: {v}")
    else:
        print(str(data))


def cmd_auth(args: argparse.Namespace) -> None:
    if args.auth_action == "login":
        if not args.key:
            print("Error: --key argument is required for login.", file=sys.stderr)
            sys.exit(1)
        config = load_config()
        config["api_key"] = args.key
        save_config(config)
        print("Authentication successful. API key saved.")
    elif args.auth_action == "status":
        config = load_config()
        key = config.get("api_key")
        if key:
            masked = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else "***"
            print(f"Authenticated with API key: {masked}")
        else:
            print("Not authenticated. Run 'evalforge auth login --key <API_KEY>'")


def cmd_projects(args: argparse.Namespace) -> None:
    client = CLIClient()
    if args.project_action == "list":
        res = client.request("GET", "/api/v1/projects", params={"page": args.page, "page_size": args.page_size})
        print_output(res.get("data", res), args.json)
    elif args.project_action == "create":
        res = client.request("POST", "/api/v1/projects", json_data={"name": args.name, "description": args.description})
        print_output(res.get("data", res), args.json)


def cmd_datasets(args: argparse.Namespace) -> None:
    client = CLIClient()
    if args.dataset_action == "list":
        res = client.request("GET", "/api/v1/datasets", params={"project_id": args.project_id})
        print_output(res.get("data", res), args.json)


def cmd_evaluations(args: argparse.Namespace) -> None:
    client = CLIClient()
    if args.eval_action == "run":
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"Error reading config file: {str(e)}", file=sys.stderr)
            sys.exit(1)

        payload = {
            "project_id": args.project_id,
            "name": config_data.get("name", "CLI Evaluation"),
            "test_cases": config_data.get("test_cases", []),
            "metrics": config_data.get("metrics", ["accuracy"]),
        }
        res = client.request("POST", "/api/v1/evaluations", json_data=payload)
        print_output(res.get("data", res), args.json)


def cmd_jobs(args: argparse.Namespace) -> None:
    client = CLIClient()
    if args.job_action == "get":
        res = client.request("GET", f"/api/v1/jobs/{args.id}")
        print_output(res.get("data", res), args.json)


def cmd_results(args: argparse.Namespace) -> None:
    client = CLIClient()
    if args.result_action == "get":
        res = client.request("GET", f"/api/v1/evaluations/{args.run_id}/results", params={"limit": args.limit})
        print_output(res.get("data", res), args.json)


def cmd_config(args: argparse.Namespace) -> None:
    if args.config_action == "set":
        config = load_config()
        if args.base_url:
            config["base_url"] = args.base_url
            save_config(config)
            print(f"Base URL set to: {args.base_url}")
    elif args.config_action == "get":
        config = load_config()
        print(json.dumps(config, indent=2))


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="evalforge",
        description="Official CLI for the Eval-Forge AI Evaluation Platform",
    )
    parser.add_argument("--json", action="store_true", help="Format output as JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Auth
    p_auth = subparsers.add_parser("auth", help="Authentication commands")
    sub_auth = p_auth.add_subparsers(dest="auth_action", required=True)
    p_login = sub_auth.add_parser("login", help="Log in with an API key")
    p_login.add_argument("--key", required=True, help="Eval-Forge API Key")
    sub_auth.add_parser("status", help="Check authentication status")

    # Projects
    p_proj = subparsers.add_parser("projects", help="Manage evaluation projects")
    sub_proj = p_proj.add_subparsers(dest="project_action", required=True)
    p_proj_list = sub_proj.add_parser("list", help="List projects")
    p_proj_list.add_argument("--page", type=int, default=1)
    p_proj_list.add_argument("--page-size", type=int, default=20)
    p_proj_create = sub_proj.add_parser("create", help="Create a project")
    p_proj_create.add_argument("--name", required=True, help="Project name")
    p_proj_create.add_argument("--description", help="Project description")

    # Datasets
    p_data = subparsers.add_parser("datasets", help="Manage datasets")
    sub_data = p_data.add_subparsers(dest="dataset_action", required=True)
    p_data_list = sub_data.add_parser("list", help="List datasets")
    p_data_list.add_argument("--project-id", required=True, help="Project UUID")

    # Evaluations
    p_eval = subparsers.add_parser("evaluations", help="Run and manage evaluations")
    sub_eval = p_eval.add_subparsers(dest="eval_action", required=True)
    p_eval_run = sub_eval.add_parser("run", help="Launch an evaluation run")
    p_eval_run.add_argument("--project-id", required=True, help="Project UUID")
    p_eval_run.add_argument("--config", required=True, help="Path to JSON evaluation config")

    # Jobs
    p_jobs = subparsers.add_parser("jobs", help="Inspect background evaluation jobs")
    sub_jobs = p_jobs.add_subparsers(dest="job_action", required=True)
    p_jobs_get = sub_jobs.add_parser("get", help="Get job details")
    p_jobs_get.add_argument("--id", required=True, help="Job UUID")

    # Results
    p_res = subparsers.add_parser("results", help="Inspect evaluation results")
    sub_res = p_res.add_subparsers(dest="result_action", required=True)
    p_res_get = sub_res.add_parser("get", help="Get evaluation run results")
    p_res_get.add_argument("--run-id", required=True, help="Run UUID")
    p_res_get.add_argument("--limit", type=int, default=50)

    # Config
    p_cfg = subparsers.add_parser("config", help="Manage CLI configuration")
    sub_cfg = p_cfg.add_subparsers(dest="config_action", required=True)
    p_cfg_set = sub_cfg.add_parser("set", help="Set configuration value")
    p_cfg_set.add_argument("--base-url", help="API Base URL")
    sub_cfg.add_parser("get", help="View current configuration")

    parsed = parser.parse_args(argv)

    if parsed.command == "auth":
        cmd_auth(parsed)
    elif parsed.command == "projects":
        cmd_projects(parsed)
    elif parsed.command == "datasets":
        cmd_datasets(parsed)
    elif parsed.command == "evaluations":
        cmd_evaluations(parsed)
    elif parsed.command == "jobs":
        cmd_jobs(parsed)
    elif parsed.command == "results":
        cmd_results(parsed)
    elif parsed.command == "config":
        cmd_config(parsed)


if __name__ == "__main__":
    main()
