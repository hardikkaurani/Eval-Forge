package sdk

import (
	"bytes"
	"io"
	"net/http"
	"strings"
	"time"
)

type EvalForgeClient struct {
	BaseURL    string
	APIKey     string
	HTTPClient *http.Client
}

func NewEvalForgeClient(baseURL string, apiKey string) *EvalForgeClient {
	return &EvalForgeClient{
		BaseURL: strings.TrimSuffix(baseURL, "/"),
		APIKey:  apiKey,
		HTTPClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

func (c *EvalForgeClient) TriggerRun(payload []byte) (string, error) {
	url := c.BaseURL + "/api/v1/evaluations/batch"
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(payload))
	if err != nil {
		return "", err
	}
	req.Header.Set("X-API-Key", c.APIKey)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	return string(body), nil
}
