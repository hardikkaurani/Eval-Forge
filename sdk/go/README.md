# Eval-Forge Go SDK (`evalforge`)

Official Go client library for the [Eval-Forge](https://github.com/hardikkaurani/Eval-Forge) AI evaluation and LLM observability platform.

---

## Installation

```bash
go get github.com/hardikkaurani/Eval-Forge/sdk/go
```

---

## Authentication

Set your API key via the `EVALFORGE_API_KEY` environment variable:

```bash
export EVALFORGE_API_KEY="ef_live_your_api_key_here"
export EVALFORGE_BASE_URL="http://localhost:8000"  # Optional, defaults to http://localhost:8000
```

Or pass it directly when initializing the client:

```go
client, err := evalforge.NewClient("ef_live_your_api_key_here")
if err != nil {
    log.Fatalf("Failed to initialize EvalForge client: %v", err)
}
```

---

## Quickstart

```go
package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/hardikkaurani/Eval-Forge/sdk/go"
)

func main() {
	// Initialize client using EVALFORGE_API_KEY or explicit key
	client, err := evalforge.NewClient("")
	if err != nil {
		log.Fatalf("Initialization error: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// List accessible evaluation projects
	projectsJSON, err := client.GetProjects(ctx)
	if err != nil {
		log.Fatalf("Failed to retrieve projects: %v", err)
	}

	fmt.Println("Projects response:")
	fmt.Println(projectsJSON)
}
```

---

## License

MIT
