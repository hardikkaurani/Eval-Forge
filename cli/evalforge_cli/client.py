import sys
from typing import Any, Dict, Optional

import httpx

from evalforge_cli.config import get_api_key, get_base_url


class CLIClient:

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or get_api_key()
        self.base_url = base_url or get_base_url()

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.api_key:
            print(
                "Error: Authentication required. Run 'evalforge auth login --key <API_KEY>' or set EVALFORGE_API_KEY.",
                file=sys.stderr,
            )
            sys.exit(1)

        url = f"{self.base_url}{path}"
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "evalforge-cli/1.0.0",
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(
                    method, url, headers=headers, params=params, json=json_data
                )
                if response.status_code == 401:
                    print("Error: Invalid or expired API key.", file=sys.stderr)
                    sys.exit(1)
                elif response.status_code == 404:
                    print(f"Error: Resource not found at {path}.", file=sys.stderr)
                    sys.exit(1)
                elif response.status_code >= 400:
                    print(
                        f"API Error ({response.status_code}): {response.text}",
                        file=sys.stderr,
                    )
                    sys.exit(1)

                return response.json()
        except httpx.ConnectError as e:
            print(
                f"Error: Could not connect to Eval-Forge server at {self.base_url}: {str(e)}",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
