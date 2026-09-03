package evalforge

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

type Client struct {
	ApiKey     string
	BaseURL    string
	HTTPClient *http.Client
}

func NewClient(apiKey string) (*Client, error) {
	if apiKey == "" {
		apiKey = os.Getenv("EVALFORGE_API_KEY")
	}
	if apiKey == "" {
		return nil, fmt.Errorf("API key must be provided or set via EVALFORGE_API_KEY")
	}

	baseURL := os.Getenv("EVALFORGE_BASE_URL")
	if baseURL == "" {
		baseURL = "http://localhost:8000"
	}
	baseURL = strings.TrimRight(baseURL, "/")

	return &Client{
		ApiKey:  apiKey,
		BaseURL: baseURL,
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}, nil
}

func (c *Client) GetProjects(ctx context.Context) (string, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", c.BaseURL+"/api/v1/projects", nil)
	if err != nil {
		return "", err
	}

	req.Header.Set("X-API-Key", c.ApiKey)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", "evalforge-go/1.0.0")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	if resp.StatusCode >= 400 {
		return "", fmt.Errorf("API error %d: %s", resp.StatusCode, string(bodyBytes))
	}

	return string(bodyBytes), nil
}
