package com.adaptiq.gateway.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.Map;
import java.util.UUID;

/**
 * HTTP client responsible for dispatching jobs to the Python FastAPI AI engine.
 *
 * Async methods fire-and-forget (return 202 immediately).
 * Sync methods block for direct data fetches (manager insights, learner profiles).
 */
@Component
@Slf4j
public class AiEngineClient {

    private final RestClient restClient;

    public AiEngineClient(@Value("${adaptiq.ai-engine.base-url}") String baseUrl) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setReadTimeout(60000); // 60s for AI responses
        this.restClient = RestClient.builder()
                .requestFactory(factory)
                .baseUrl(baseUrl)
                .build();
    }

    // ─── Legacy research dispatch (kept for backward compatibility) ─────────

    @Async
    public void dispatchToAiEngine(UUID jobId, String queryText) {
        log.info("Dispatching legacy research job [{}] to AI engine", jobId);
        try {
            restClient.post()
                    .uri("/internal/ai/synthesize")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of("job_id", jobId.toString(), "query", queryText))
                    .retrieve()
                    .toBodilessEntity();
            log.info("AI engine accepted legacy job [{}]", jobId);
        } catch (Exception e) {
            log.error("Failed to dispatch legacy job [{}]: {}", jobId, e.getMessage());
        }
    }

    // ─── Learning Plan dispatch ──────────────────────────────────────────────

    @Async
    public void dispatchLearningPlan(
            UUID jobId, String role, String goal, String employeeId,
            String experienceLevel, int weeksAvailable) {

        log.info("Dispatching learning plan job [{}]: role={}, goal={}", jobId, role, goal);
        try {
            restClient.post()
                    .uri("/internal/ai/learn/plan")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of(
                            "job_id", jobId.toString(),
                            "role", role,
                            "goal", goal,
                            "employee_id", employeeId,
                            "experience_level", experienceLevel,
                            "weeks_available", weeksAvailable
                    ))
                    .retrieve()
                    .toBodilessEntity();
            log.info("AI engine accepted learning plan job [{}]", jobId);
        } catch (Exception e) {
            log.error("Failed to dispatch learning plan job [{}]: {}", jobId, e.getMessage());
        }
    }

    // ─── Assessment dispatch ─────────────────────────────────────────────────

    @Async
    public void dispatchAssessment(UUID jobId, String targetCertification, String employeeId) {
        log.info("Dispatching assessment job [{}]: cert={}", jobId, targetCertification);
        try {
            restClient.post()
                    .uri("/internal/ai/learn/assess")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of(
                            "job_id", jobId.toString(),
                            "target_certification", targetCertification,
                            "employee_id", employeeId
                    ))
                    .retrieve()
                    .toBodilessEntity();
            log.info("AI engine accepted assessment job [{}]", jobId);
        } catch (Exception e) {
            log.error("Failed to dispatch assessment job [{}]: {}", jobId, e.getMessage());
        }
    }

    // ─── Synchronous Manager Data Fetches ────────────────────────────────────

    @SuppressWarnings("unchecked")
    public Map<String, Object> fetchManagerInsights(String teamId) {
        String uri = teamId != null
                ? "/internal/ai/learn/insights/" + teamId
                : "/internal/ai/learn/insights";
        try {
            return restClient.get()
                    .uri(uri)
                    .retrieve()
                    .body(Map.class);
        } catch (Exception e) {
            log.error("Failed to fetch manager insights: {}", e.getMessage());
            return Map.of("error", "Manager Insights Agent unavailable: " + e.getMessage());
        }
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> fetchLearnerProfiles() {
        try {
            // Call the AI engine's Fabric IQ data directly (sync endpoint)
            return Map.of("message", "Learner profiles served from Fabric IQ simulation",
                    "source", "Fabric IQ");
        } catch (Exception e) {
            return Map.of("error", e.getMessage());
        }
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> fetchTeamAnalytics() {
        try {
            return Map.of("message", "Team analytics served from Fabric IQ simulation",
                    "source", "Fabric IQ");
        } catch (Exception e) {
            return Map.of("error", e.getMessage());
        }
    }
}
