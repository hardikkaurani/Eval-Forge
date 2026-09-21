package evalforge

import (
	"context"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"
)

func TestNewClientValidation(t *testing.T) {
	origKey := os.Getenv("EVALFORGE_API_KEY")
	os.Unsetenv("EVALFORGE_API_KEY")
	defer func() {
		if origKey != "" {
			os.Setenv("EVALFORGE_API_KEY", origKey)
		}
	}()

	_, err := NewClient("")
	if err == nil {
		t.Fatal("expected error when API key is not provided and env var is unset")
	}

	client, err := NewClient("ef_live_test_key")
	if err != nil {
		t.Fatalf("unexpected error initializing client: %v", err)
	}
	if client.ApiKey != "ef_live_test_key" {
		t.Errorf("expected ApiKey to be ef_live_test_key, got %s", client.ApiKey)
	}
	if client.BaseURL != "http://localhost:8000" {
		t.Errorf("expected default BaseURL http://localhost:8000, got %s", client.BaseURL)
	}
}

func TestGetProjectsMock(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("X-API-Key") != "ef_live_mock_key" {
			http.Error(w, `{"success": false, "message": "unauthorized"}`, http.StatusUnauthorized)
			return
		}
		if r.URL.Path != "/api/v1/projects" {
			http.NotFound(w, r)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"success": true, "data": [{"id": "proj-1", "name": "Test Project"}]}`))
	}))
	defer server.Close()

	client, err := NewClient("ef_live_mock_key")
	if err != nil {
		t.Fatalf("failed to create client: %v", err)
	}
	client.BaseURL = server.URL

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	resp, err := client.GetProjects(ctx)
	if err != nil {
		t.Fatalf("expected successful GetProjects, got: %v", err)
	}
	if resp == "" {
		t.Fatal("expected non-empty response body")
	}
}
