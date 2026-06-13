package com.adaptiq.gateway.controller;

import com.adaptiq.gateway.dto.AiCompletionCallback;
import com.adaptiq.gateway.service.ResearchService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

/**
 * Internal controller for inter-service communication.
 * Only the FastAPI AI engine should call these endpoints.
 * In production, this would be secured via internal network rules or mTLS.
 */
@RestController
@RequestMapping("/internal")
@RequiredArgsConstructor
@Slf4j
public class InternalController {

    private final ResearchService researchService;

    /**
     * Callback endpoint invoked by the AI engine when a job completes.
     * Saves the report, trace logs, and marks the job as completed.
     */
    @PostMapping("/jobs/{jobId}/complete")
    public ResponseEntity<Void> completeJob(
            @PathVariable UUID jobId,
            @Valid @RequestBody AiCompletionCallback callback) {

        log.info("Received completion callback for job [{}]", jobId);
        researchService.completeJob(jobId, callback);
        return ResponseEntity.ok().build();
    }

    /**
     * Callback endpoint for the AI engine to report a failure.
     */
    @PostMapping("/jobs/{jobId}/fail")
    public ResponseEntity<Void> failJob(
            @PathVariable UUID jobId,
            @RequestBody java.util.Map<String, String> body) {

        String errorMessage = body.getOrDefault("error", "Unknown error from AI engine");
        log.warn("Received failure callback for job [{}]: {}", jobId, errorMessage);
        researchService.failJob(jobId, errorMessage);
        return ResponseEntity.ok().build();
    }
}
