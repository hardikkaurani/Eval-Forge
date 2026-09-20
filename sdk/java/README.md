# Eval-Forge Java SDK (`evalforge-sdk`)

Official Java 17+ client library for the [Eval-Forge](https://github.com/hardikkaurani/Eval-Forge) AI evaluation and LLM observability platform.

---

## Installation

### Maven
Add the dependency to your `pom.xml`:

```xml
<dependency>
    <groupId>com.evalforge</groupId>
    <artifactId>evalforge-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Gradle
```groovy
implementation 'com.evalforge:evalforge-sdk:1.0.0'
```

---

## Authentication

Set your API key via the `EVALFORGE_API_KEY` environment variable:

```bash
export EVALFORGE_API_KEY="ef_live_your_api_key_here"
export EVALFORGE_BASE_URL="http://localhost:8000"  # Optional, defaults to http://localhost:8000
```

Or pass it via the client builder:

```java
import com.evalforge.EvalForgeClient;

EvalForgeClient client = EvalForgeClient.builder()
        .apiKey("ef_live_your_api_key_here")
        .baseUrl("http://localhost:8000") // Optional
        .timeoutSeconds(30)               // Optional
        .build();
```

---

## Quickstart

```java
import com.evalforge.EvalForgeClient;

public class Main {
    public static void main(String[] args) {
        try {
            EvalForgeClient client = EvalForgeClient.builder()
                    .apiKey(System.getenv("EVALFORGE_API_KEY"))
                    .build();

            String projectsJson = client.getProjects();
            System.out.println("Projects response: " + projectsJson);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

## License

MIT
