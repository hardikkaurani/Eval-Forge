package com.evalforge;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public class EvalForgeClient {
    private final String apiKey;
    private final String baseUrl;
    private final HttpClient httpClient;

    private EvalForgeClient(Builder builder) {
        this.apiKey = builder.apiKey;
        this.baseUrl = builder.baseUrl.replaceAll("/$", "");
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(builder.timeoutSeconds))
                .build();
    }

    public static Builder builder() {
        return new Builder();
    }

    public String getProjects() throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/v1/projects"))
                .header("X-API-Key", apiKey)
                .header("Content-Type", "application/json")
                .header("User-Agent", "evalforge-java/1.0.0")
                .GET()
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public static class Builder {
        private String apiKey = System.getenv("EVALFORGE_API_KEY");
        private String baseUrl = System.getenv().getOrDefault("EVALFORGE_BASE_URL", "http://localhost:8000");
        private int timeoutSeconds = 30;

        public Builder apiKey(String apiKey) {
            this.apiKey = apiKey;
            return this;
        }

        public Builder baseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
            return this;
        }

        public Builder timeoutSeconds(int timeoutSeconds) {
            this.timeoutSeconds = timeoutSeconds;
            return this;
        }

        public EvalForgeClient build() {
            if (apiKey == null || apiKey.isBlank()) {
                throw new IllegalStateException("API key must be provided or configured via EVALFORGE_API_KEY");
            }
            return new EvalForgeClient(this);
        }
    }
}
