package com.adaptiq.gateway.controller;

import com.adaptiq.gateway.dto.JobAcceptedResponse;
import com.adaptiq.gateway.dto.JobStatusResponse;
import com.adaptiq.gateway.service.LearningService;
import com.adaptiq.gateway.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Public-facing REST controller for Enterprise Learning operations.
 *
 * POST /api/v1/learn/plan      — Submit a learning plan request (Curator + Study Plan agents)
 * POST /api/v1/learn/assess    — Submit an assessment request (Assessment Agent)
 * GET  /api/v1/learn/jobs/{id} — Poll job status and result
 * GET  /api/v1/learn/jobs      — Get learning job history for the authenticated user
 *
 * All endpoints require a valid JWT. Users can only access their own jobs.
 */
@RestController
@RequestMapping("/api/v1/learn")
@RequiredArgsConstructor
@Slf4j
public class LearningController {

    private final LearningService learningService;
    private final JwtTokenProvider jwtTokenProvider;

    /**
     * Submit a learning plan request.
     * The authenticated user's role and employeeId are extracted from the JWT — not from the request body.
     */
    @PostMapping("/plan")
    public ResponseEntity<JobAcceptedResponse> submitLearningPlan(
            @RequestBody Map<String, Object> request,
            Authentication authentication) {

        UUID userId = UUID.fromString(authentication.getName());
        String token = (String) authentication.getCredentials();
        String employeeId = jwtTokenProvider.extractEmployeeId(token);

        String role = (String) request.getOrDefault("role", "Cloud Engineer");
        String goal = (String) request.getOrDefault("goal", "Get certified");
        String experienceLevel = (String) request.getOrDefault("experienceLevel", "intermediate");
        int weeksAvailable = request.containsKey("weeksAvailable")
                ? Integer.parseInt(request.get("weeksAvailable").toString()) : 6;

        UUID jobId = learningService.submitLearningPlan(role, goal, employeeId, experienceLevel, weeksAvailable, userId);

        return ResponseEntity.status(HttpStatus.ACCEPTED).body(
                JobAcceptedResponse.builder()
                        .jobId(jobId)
                        .status("processing")
                        .message("Learning plan pipeline started. Poll /api/v1/learn/jobs/" + jobId + " for results.")
                        .build()
        );
    }

    /**
     * Submit an assessment request.
     */
    @PostMapping("/assess")
    public ResponseEntity<JobAcceptedResponse> submitAssessment(
            @RequestBody Map<String, Object> request,
            Authentication authentication) {

        UUID userId = UUID.fromString(authentication.getName());
        String token = (String) authentication.getCredentials();
        String employeeId = jwtTokenProvider.extractEmployeeId(token);

        String targetCertification = (String) request.getOrDefault("targetCertification", "AZ-204");

        UUID jobId = learningService.submitAssessment(targetCertification, employeeId, userId);

        return ResponseEntity.status(HttpStatus.ACCEPTED).body(
                JobAcceptedResponse.builder()
                        .jobId(jobId)
                        .status("processing")
                        .message("Assessment pipeline started. Poll /api/v1/learn/jobs/" + jobId + " for results.")
                        .build()
        );
    }

    /**
     * Poll for a specific job status and result.
     */
    @GetMapping("/jobs/{jobId}")
    public ResponseEntity<JobStatusResponse> getJobStatus(@PathVariable UUID jobId) {
        return ResponseEntity.ok(learningService.getJobStatus(jobId));
    }

    /**
     * Get learning job history for the authenticated user.
     */
    @GetMapping("/jobs")
    public ResponseEntity<List<JobStatusResponse>> getJobHistory(Authentication authentication) {
        UUID userId = UUID.fromString(authentication.getName());
        return ResponseEntity.ok(learningService.getJobHistory(userId));
    }

    /**
     * Delete a specific job from history.
     */
    @DeleteMapping("/jobs/{jobId}")
    public ResponseEntity<Void> deleteJob(@PathVariable UUID jobId, Authentication authentication) {
        UUID userId = UUID.fromString(authentication.getName());
        learningService.deleteJob(jobId, userId);
        return ResponseEntity.noContent().build();
    }
}
