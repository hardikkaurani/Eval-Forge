// Eval-Forge Java SDK Quickstart Example
// Compile and run with Java 17+:
// javac -cp "sdk/java/target/evalforge-sdk-1.0.0.jar:sdk/java/target/dependency/*" examples/JavaQuickstart.java
// java -cp ".:sdk/java/target/evalforge-sdk-1.0.0.jar:sdk/java/target/dependency/*" JavaQuickstart

import com.evalforge.EvalForgeClient;

public class JavaQuickstart {
    public static void main(String[] args) {
        String apiKey = System.getenv("EVALFORGE_API_KEY");
        if (apiKey == null || apiKey.isBlank()) {
            apiKey = "ef_live_example_key";
        }
        String baseUrl = System.getenv("EVALFORGE_BASE_URL");
        if (baseUrl == null || baseUrl.isBlank()) {
            baseUrl = "http://localhost:8000";
        }

        System.out.println("==================================================");
        System.out.println("🚀 Eval-Forge Java SDK — Hello EvalForge");
        System.out.println("Target Base URL: " + baseUrl);
        System.out.println("==================================================");

        try {
            EvalForgeClient client = EvalForgeClient.builder()
                    .apiKey(apiKey)
                    .baseUrl(baseUrl)
                    .timeoutSeconds(10)
                    .build();

            System.out.println("\nListing accessible projects...");
            String projectsJson = client.getProjects();
            System.out.println("✓ Projects Response:");
            System.out.println(projectsJson);
        } catch (Exception e) {
            System.out.println("Notice: Could not connect to " + baseUrl + " (" + e.getMessage() + ")");
            System.out.println("Ensure the EvalForge backend is running on http://localhost:8000");
        }
    }
}
