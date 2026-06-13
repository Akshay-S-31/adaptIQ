package com.adaptiq.gateway.controller;

import com.adaptiq.gateway.dto.JobAcceptedResponse;
import com.adaptiq.gateway.dto.JobStatusResponse;
import com.adaptiq.gateway.dto.ResearchQueryRequest;
import com.adaptiq.gateway.service.ResearchService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

/**
 * Public-facing REST controller for research operations.
 * All endpoints require a valid JWT. The authenticated user's ID
 * is extracted from the token — users can only access their own data.
 */
@RestController
@RequestMapping("/api/v1/research")
@RequiredArgsConstructor
@Slf4j
public class ResearchController {

    private final ResearchService researchService;

    /**
     * Accepts a new research query and kicks off the async AI pipeline.
     * The query is linked to the authenticated user.
     */
    @PostMapping("/query")
    public ResponseEntity<JobAcceptedResponse> submitQuery(
            @Valid @RequestBody ResearchQueryRequest request,
            Authentication authentication) {

        UUID userId = UUID.fromString(authentication.getName());
        UUID jobId = researchService.submitQuery(request.getQuery(), userId);

        JobAcceptedResponse response = JobAcceptedResponse.builder()
                .jobId(jobId)
                .status("processing")
                .message("Research query accepted. Poll /api/v1/research/jobs/" + jobId + " for results.")
                .build();

        return ResponseEntity.status(HttpStatus.ACCEPTED).body(response);
    }

    /**
     * Polling endpoint for clients to check job status.
     */
    @GetMapping("/jobs/{jobId}")
    public ResponseEntity<JobStatusResponse> getJobStatus(@PathVariable UUID jobId) {
        JobStatusResponse status = researchService.getJobStatus(jobId);
        return ResponseEntity.ok(status);
    }

    /**
     * Returns the authenticated user's job history only.
     */
    @GetMapping("/jobs")
    public ResponseEntity<List<JobStatusResponse>> getJobHistory(Authentication authentication) {
        UUID userId = UUID.fromString(authentication.getName());
        return ResponseEntity.ok(researchService.getJobHistory(userId));
    }
}
