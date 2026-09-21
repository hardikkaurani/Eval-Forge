#!/usr/bin/env bash
"""Evalium Environment & Dependency Doctor.

Comprehensive audit tool verifying toolchain compatibility, dependency integrity,
environment configuration, and production safety rules without leaking secrets.
"""

from __future__ import annotations

import argparse
import importlib
from pathlib import Path
import re
import shutil
import subprocess  # nosec B404
import sys
from urllib.parse import urlparse

# Ensure backend is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def mask_connection_url(raw_url: str | None) -> str:
    """Safely mask credentials in connection URLs so secrets are never printed."""
    if not raw_url:
        return "[NOT CONFIGURED]"
    try:
        parsed = urlparse(raw_url)
        if parsed.password:
            safe_netloc = parsed.netloc.replace(f":{parsed.password}@", ":***@")
            masked = parsed._replace(netloc=safe_netloc).geturl()
            return masked
        return raw_url
    except Exception:
        return "[CONFIGURED (MASKED)]"


class EnvironmentDoctor:
    def __init__(self, target_env: str | None = None) -> None:
        self.root_dir = ROOT_DIR
        self.backend_dir = BACKEND_DIR
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checks: list[tuple[str, bool, str]] = []

        # Target environment resolution
        if target_env:
            self.app_env = target_env.lower()
        else:
            try:
                from app.config.config import settings

                self.app_env = (settings.APP_ENV or "development").lower()
            except Exception:
                self.app_env = "development"

    def record_check(self, name: str, success: bool, message: str) -> None:
        self.checks.append((name, success, message))
        if not success:
            self.errors.append(f"{name}: {message}")

    def check_python_version(self) -> bool:
        ver = sys.version_info
        is_valid = ver >= (3, 12)
        v_str = f"{ver[0]}.{ver[1]}.{ver[2]}"
        msg = f"Python {v_str} detected (minimum required >= 3.12)"
        self.record_check("Python Runtime", is_valid, msg)
        return is_valid

    def check_node_version(self) -> bool:
        node_bin = shutil.which("node")
        if not node_bin:
            self.record_check(
                "Node.js Runtime", False, "Node.js executable not found on PATH"
            )
            return False
        try:
            res = subprocess.run(
                [node_bin, "--version"], capture_output=True, text=True, timeout=5
            )  # nosec B603
            version_match = re.search(r"v?(\d+)\.", res.stdout.strip())
            if version_match:
                major = int(version_match.group(1))
                is_valid = major >= 20
                self.record_check(
                    "Node.js Runtime",
                    is_valid,
                    f"Node {res.stdout.strip()} detected (required >= 20, recommended 22)",
                )
                return is_valid
        except Exception as exc:
            self.record_check(
                "Node.js Runtime", False, f"Failed to execute node: {exc}"
            )
            return False
        self.record_check("Node.js Runtime", False, "Unknown node version format")
        return False

    def check_package_manager(self) -> bool:
        npm_bin = shutil.which("npm")
        if not npm_bin:
            self.record_check(
                "Package Manager", False, "npm executable not found on PATH"
            )
            return False
        try:
            res = subprocess.run(
                [npm_bin, "--version"], capture_output=True, text=True, timeout=5
            )  # nosec B603
            v_str = res.stdout.strip()
            self.record_check("Package Manager", True, f"npm v{v_str} detected")
            return True
        except Exception as exc:
            self.record_check("Package Manager", False, f"Failed to execute npm: {exc}")
            return False

    def check_core_dependencies(self) -> bool:
        required_modules = [
            ("fastapi", "FastAPI"),
            ("uvicorn", "Uvicorn"),
            ("pydantic", "Pydantic"),
            ("pydantic_settings", "Pydantic Settings"),
            ("sqlalchemy", "SQLAlchemy"),
            ("alembic", "Alembic"),
            ("celery", "Celery"),
            ("redis", "Redis Client"),
            ("jwt", "PyJWT"),
            ("anyio", "AnyIO"),
            ("structlog", "Structlog"),
            ("httpx", "HTTPX"),
            ("stripe", "Stripe SDK"),
        ]
        all_passed = True
        failed_modules = []
        for mod, name in required_modules:
            try:
                importlib.import_module(mod)
            except Exception as e:
                all_passed = False
                failed_modules.append(f"{name} ({mod}: {e})")

        if all_passed:
            self.record_check(
                "Core Dependencies",
                True,
                f"All {len(required_modules)} core runtime packages importable",
            )
        else:
            self.record_check(
                "Core Dependencies",
                False,
                f"Missing packages: {', '.join(failed_modules)}",
            )
        return all_passed

    def check_sdk_and_cli_packages(self) -> bool:
        passed = True
        details = []
        try:
            import evalforge.models  # noqa: F401

            details.append("evalforge SDK")
        except Exception as exc:
            passed = False
            details.append(f"evalforge SDK error: {exc}")

        try:
            import evalforge_cli.main  # noqa: F401

            details.append("evalforge CLI")
        except Exception as exc:
            passed = False
            details.append(f"evalforge CLI error: {exc}")

        self.record_check("SDK & CLI Modules", passed, " | ".join(details))
        return passed

    def check_configuration_and_security(self, custom_settings=None) -> bool:
        try:
            from app.config.config import settings, _is_insecure_credential

            current_settings = custom_settings or settings
            is_prod = self.app_env == "production"

            # 1. Database
            db_url = current_settings.get_database_url
            masked_db = mask_connection_url(db_url)
            parsed_db = urlparse(db_url)
            if is_prod and (
                parsed_db.scheme.startswith("sqlite")
                or parsed_db.hostname in ("localhost", "127.0.0.1", "::1")
            ):
                self.record_check(
                    "Database Configuration",
                    False,
                    f"Localhost/SQLite database disallowed in production: {masked_db}",
                )
            else:
                self.record_check(
                    "Database Configuration", True, f"CONFIGURED ({masked_db})"
                )

            # 2. Redis
            redis_url = current_settings.get_redis_url
            masked_redis = mask_connection_url(redis_url)
            parsed_redis = urlparse(redis_url)
            if is_prod and (parsed_redis.hostname in ("localhost", "127.0.0.1", "::1")):
                self.record_check(
                    "Redis Configuration",
                    False,
                    f"Localhost Redis disallowed in production: {masked_redis}",
                )
            else:
                self.record_check(
                    "Redis Configuration", True, f"CONFIGURED ({masked_redis})"
                )

            # 3. Secret Key
            sec_val = current_settings.SECRET_KEY.get_secret_value()
            if is_prod and (
                _is_insecure_credential(sec_val)
                or sec_val == "dev-secret-key-evalforge-placeholder"
                or len(sec_val) < 16
            ):
                self.record_check(
                    "Secret Key Security",
                    False,
                    "Insecure or placeholder SECRET_KEY in production",
                )
            else:
                self.record_check(
                    "Secret Key Security",
                    True,
                    f"CONFIGURED (entropy length: {len(sec_val)})",
                )

            # 4. CORS Origins
            cors = current_settings.CORS_ORIGINS
            if is_prod and ("*" in cors):
                self.record_check(
                    "CORS Configuration",
                    False,
                    "Wildcard '*' disallowed in production CORS",
                )
            else:
                self.record_check(
                    "CORS Configuration",
                    True,
                    f"{len(cors)} trusted origins configured",
                )

            # 5. Google OAuth
            if current_settings.GOOGLE_CLIENT_ID:
                has_secret = bool(
                    current_settings.GOOGLE_CLIENT_SECRET
                    and not _is_insecure_credential(
                        current_settings.GOOGLE_CLIENT_SECRET.get_secret_value()
                    )
                )
                valid_redirect = (
                    current_settings.GOOGLE_REDIRECT_URI.startswith("https://")
                    if is_prod
                    else True
                )
                if not has_secret:
                    self.record_check(
                        "Google OAuth",
                        False,
                        "GOOGLE_CLIENT_ID configured but GOOGLE_CLIENT_SECRET missing/insecure",
                    )
                elif not valid_redirect:
                    self.record_check(
                        "Google OAuth",
                        False,
                        f"GOOGLE_REDIRECT_URI must use HTTPS in production: {current_settings.GOOGLE_REDIRECT_URI}",
                    )
                else:
                    self.record_check(
                        "Google OAuth",
                        True,
                        f"CONFIGURED (Redirect URI: {current_settings.GOOGLE_REDIRECT_URI})",
                    )
            else:
                self.record_check("Google OAuth", True, "Optional (Not configured)")

            return len(self.errors) == 0

        except Exception as exc:
            self.record_check(
                "Configuration & Security", False, f"Settings evaluation error: {exc}"
            )
            return False

    def check_alembic_migrations(self) -> bool:
        try:
            from alembic.config import Config
            from alembic.script import ScriptDirectory

            alembic_ini_path = self.backend_dir / "alembic.ini"
            if not alembic_ini_path.exists():
                self.record_check(
                    "Alembic Migrations", False, "backend/alembic.ini not found"
                )
                return False

            cfg = Config(str(alembic_ini_path))
            script = ScriptDirectory.from_config(cfg)
            heads = script.get_heads()
            if len(heads) == 1:
                self.record_check(
                    "Alembic Migrations",
                    True,
                    f"Single migration head validated ({heads[0]})",
                )
                return True
            else:
                self.record_check(
                    "Alembic Migrations",
                    False,
                    f"Multiple migration heads detected: {heads}",
                )
                return False
        except Exception as exc:
            self.record_check(
                "Alembic Migrations", False, f"Migration inspection failed: {exc}"
            )
            return False

    def run_all(self) -> bool:
        self.check_python_version()
        self.check_node_version()
        self.check_package_manager()
        self.check_core_dependencies()
        self.check_sdk_and_cli_packages()
        self.check_configuration_and_security()
        self.check_alembic_migrations()
        return len(self.errors) == 0

    def format_report(self) -> str:
        lines = []
        lines.append("=" * 64)
        lines.append(
            f" Evalium Environment Doctor (Target Environment: {self.app_env})"
        )
        lines.append("=" * 64)
        for name, ok, msg in self.checks:
            tag = "[PASS]" if ok else "[FAIL]"
            lines.append(f"{tag:<7} {name}: {msg}")
        lines.append("-" * 64)
        if not self.errors:
            lines.append("RESULT: ALL AUDIT GATES PASSED (100% HEALTHY).")
        else:
            lines.append(f"RESULT: {len(self.errors)} AUDIT FAILURE(S) DETECTED:")
            for err in self.errors:
                lines.append(f"  - {err}")
        lines.append("=" * 64)
        return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalium Environment Doctor")
    parser.add_argument(
        "--env",
        choices=["development", "testing", "production"],
        default=None,
        help="Target environment to validate",
    )
    args = parser.parse_args()

    doctor = EnvironmentDoctor(target_env=args.env)
    success = doctor.run_all()
    print(doctor.format_report())
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
