from fastapi import APIRouter
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/playground", tags=["Developer Platform - Playground"])


@router.post("/generate-code", response_model=ApiResponse[dict])
async def generate_sdk_snippets(
    endpoint: str,
    method: str = "POST",
    payload_sample: dict = None
):
    """Generates boilerplate integration code for Python, TypeScript, Go, and Java clients."""
    python_code = f"""import requests

url = "https://api.evalforge.com/api/v1/public{endpoint}"
headers = {{
    "X-API-Key": "your_api_key_here",
    "Content-Type": "application/json"
}}
response = requests.{method.lower()}(url, json={payload_sample or {}}, headers=headers)
print(response.json())
"""

    ts_code = f"""import axios from 'axios';

const url = 'https://api.evalforge.com/api/v1/public{endpoint}';
const headers = {{
  'X-API-Key': 'your_api_key_here',
  'Content-Type': 'application/json'
}};
axios.{method.lower()}(url, {payload_sample or {}}, {{ headers }})
  .then(res => console.log(res.data))
  .catch(err => console.error(err));
"""

    go_code = f"""package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

func main() {{
	url := "https://api.evalforge.com/api/v1/public{endpoint}"
	payload, _ := json.Marshal({payload_sample or map[string]string{{}}})
	req, _ := http.NewRequest("{method}", url, bytes.NewBuffer(payload))
	req.Header.Set("X-API-Key", "your_api_key_here")
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{{}}
	resp, _ := client.Do(req)
	defer resp.Body.Close()
	fmt.Println("Status Code:", resp.StatusCode)
}}
"""

    java_code = f"""import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class Main {{
    public static void main(String[] args) throws Exception {{
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://api.evalforge.com/api/v1/public{endpoint}"))
            .header("X-API-Key", "your_api_key_here")
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString("{json_dumps(payload_sample) if payload_sample else "{}"}"))
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
            "java": java_code
        }
    )


import json # Ensure json is imported
def json_dumps(d):
    return json.dumps(d).replace('"', '\\"')
