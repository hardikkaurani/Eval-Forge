import json
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from app.platform.schemas import (
    PlaygroundExecuteRequest,
    PlaygroundExecuteResponse,
)
from app.platform.services.playground_proxy import playground_proxy_service
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/playground", tags=["Developer Platform - Playground"])


class CodeGenerationRequest(BaseModel):
    endpoint: str
    method: str = "POST"
    payload_sample: Optional[dict] = None


@router.post("/execute", response_model=ApiResponse[PlaygroundExecuteResponse])
async def execute_playground_request(
    req: PlaygroundExecuteRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """Executes an allowlisted API request in the playground with SSRF defenses."""
    try:
        res = playground_proxy_service.execute_request(
            endpoint=req.endpoint,
            method=req.method,
            payload=req.payload,
            headers=req.headers,
            api_key=x_api_key,
        )
        return create_response(
            True, "Request executed successfully.", PlaygroundExecuteResponse(**res)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Playground execution error: {str(e)}",
        ) from e


@router.post("/generate-code", response_model=ApiResponse[dict])
async def generate_sdk_snippets(req: CodeGenerationRequest):
    """Generates integration code snippets for Python, TypeScript, Go, and Java."""
    endpoint = req.endpoint
    method = req.method.upper()
    payload_sample = req.payload_sample
    p_val = payload_sample or {}

    python_code = f"""import requests

url = "https://api.evalforge.com/api/v1{endpoint}"
headers = {{
    "X-API-Key": "your_api_key_here",
    "Content-Type": "application/json"
}}
response = requests.{method.lower()}(url, json={p_val}, headers=headers)
print(response.json())
"""

    ts_code = f"""import axios from 'axios';

const url = 'https://api.evalforge.com/api/v1{endpoint}';
const headers = {{
  'X-API-Key': 'your_api_key_here',
  'Content-Type': 'application/json'
}};
axios.{method.lower()}(url, {p_val}, {{ headers }})
  .then(res => console.log(res.data))
  .catch(err => console.error(err));
"""

    go_payload = json.dumps(payload_sample) if payload_sample else "map[string]string{}"
    go_code = f"""package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

func main() {{
	url := "https://api.evalforge.com/api/v1{endpoint}"
	payload, _ := json.Marshal({go_payload})
	req, _ := http.NewRequest("{method}", url, bytes.NewBuffer(payload))
	req.Header.Set("X-API-Key", "your_api_key_here")
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{{}}
	resp, _ := client.Do(req)
	defer resp.Body.Close()
	fmt.Println("Status Code:", resp.StatusCode)
}}
"""

    java_payload = (
        json.dumps(payload_sample).replace('"', '\\"') if payload_sample else "{}"
    )
    java_code = f"""import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class Main {{
    public static void main(String[] args) throws Exception {{
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://api.evalforge.com/api/v1{endpoint}"))
            .header("X-API-Key", "your_api_key_here")
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString("{java_payload}"))
            .build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        System.out.println(response.body());
    }}
}}
"""

    return create_response(
        True,
        "Code snippets generated successfully.",
        {
            "python": python_code,
            "typescript": ts_code,
            "go": go_code,
            "java": java_code,
        },
    )
