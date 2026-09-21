// Eval-Forge Go SDK Quickstart Example
// Run with: go run examples/go_quickstart.go
package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/hardikkaurani/Eval-Forge/sdk/go"
)

func main() {
	apiKey := os.Getenv("EVALFORGE_API_KEY")
	if apiKey == "" {
		apiKey = "ef_live_example_key"
	}
	baseURL := os.Getenv("EVALFORGE_BASE_URL")
	if baseURL == "" {
		baseURL = "http://localhost:8000"
	}

	fmt.Println("==================================================")
	fmt.Println("🚀 Eval-Forge Go SDK — Hello EvalForge")
	fmt.Printf("Target Base URL: %s\n", baseURL)
	fmt.Println("==================================================")

	client, err := evalforge.NewClient(apiKey)
	if err != nil {
		log.Fatalf("Failed to initialize EvalForge client: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	fmt.Println("\nListing accessible projects...")
	projects, err := client.GetProjects(ctx)
	if err != nil {
		fmt.Printf("Notice: Could not connect to %s (%v)\n", baseURL, err)
		fmt.Println("Ensure the EvalForge backend is running on http://localhost:8000")
		return
	}

	fmt.Println("✓ Projects Response:")
	fmt.Println(projects)
}
