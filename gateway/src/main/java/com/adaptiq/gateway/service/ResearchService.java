package com.adaptiq.gateway.service;

import com.adaptiq.gateway.dto.AiCompletionCallback;
import com.adaptiq.gateway.dto.JobStatusResponse;
import com.adaptiq.gateway.entity.AgentTrace;
import com.adaptiq.gateway.entity.Query;
import com.adaptiq.gateway.entity.ResearchReport;
import com.adaptiq.gateway.entity.User;
import com.adaptiq.gateway.repository.AgentTraceRepository;
import com.adaptiq.gateway.repository.QueryRepository;
import com.adaptiq.gateway.repository.ResearchReportRepository;
import com.adaptiq.gateway.repository.UserRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Duration;
import java.util.List;
import java.util.UUID;

/**
 * Core business logic for managing research jobs.
 * Every query is associated with the authenticated user.
 * History is scoped per-user — users can only see their own jobs.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ResearchService {

    private final QueryRepository queryRepository;
    private final ResearchReportRepository reportRepository;
    private final AgentTraceRepository traceRepository;
    private final UserRepository userRepository;
    private final AiEngineClient aiEngineClient;
    private final StringRedisTemplate redisTemplate;

    /**
     * Creates a new research query linked to the authenticated user
     * and asynchronously dispatches it to the AI engine.
     */
    @Transactional
    public UUID submitQuery(String rawPrompt, UUID userId) {
        String cacheKey = "query_cache:" + hashPrompt(rawPrompt);
        String cachedJobId = redisTemplate.opsForValue().get(cacheKey);

        if (cachedJobId != null) {
            log.info("Cache hit for prompt! Returning existing jobId: {}", cachedJobId);
            return UUID.fromString(cachedJobId);
        }

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new EntityNotFoundException("User not found: " + userId));

        Query query = Query.builder()
                .rawPrompt(rawPrompt)
                .status("processing")
                .user(user)
                .build();
        query = queryRepository.save(query);

        log.info("Created research job [{}] for user [{}], prompt: {}", query.getId(), userId,
                rawPrompt.substring(0, Math.min(rawPrompt.length(), 80)));

        // Fire-and-forget async call to the Python AI engine
        aiEngineClient.dispatchToAiEngine(query.getId(), rawPrompt);

        return query.getId();
    }

    /**
     * Retrieves the current status and (if available) the full report for a given job.
     */
    @Transactional(readOnly = true)
    public JobStatusResponse getJobStatus(UUID jobId) {
        Query query = queryRepository.findById(jobId)
                .orElseThrow(() -> new EntityNotFoundException("Job not found: " + jobId));

        JobStatusResponse.JobStatusResponseBuilder builder = JobStatusResponse.builder()
                .jobId(query.getId())
                .status(query.getStatus())
                .rawPrompt(query.getRawPrompt())
                .createdAt(query.getCreatedAt());

        if ("completed".equals(query.getStatus())) {
            reportRepository.findByQueryId(jobId).ifPresent(report -> {
                builder.executiveSummary(report.getExecutiveSummary())
                        .detailedContent(report.getDetailedContent())
                        .confidenceScore(report.getConfidenceScore())
                        .citations(report.getCitations())
                        .iterationCount(report.getIterationCount())
                        .processingTimeMs(report.getProcessingTimeMs());
            });
        } else if ("failed".equals(query.getStatus())) {
            builder.errorMessage(query.getErrorMessage());
        }

        return builder.build();
    }

    /**
     * Retrieves job history for the authenticated user only.
     * Users can NEVER see other users' jobs.
     */
    @Transactional(readOnly = true)
    public List<JobStatusResponse> getJobHistory(UUID userId) {
        return queryRepository.findByUserIdOrderByCreatedAtDesc(userId).stream()
            .map(q -> {
                JobStatusResponse.JobStatusResponseBuilder b = JobStatusResponse.builder()
                    .jobId(q.getId())
                    .status(q.getStatus())
                    .rawPrompt(q.getRawPrompt())
                    .createdAt(q.getCreatedAt());
                if ("completed".equals(q.getStatus())) {
                    reportRepository.findByQueryId(q.getId()).ifPresent(report -> {
                        b.confidenceScore(report.getConfidenceScore());
                    });
                } else if ("failed".equals(q.getStatus())) {
                    b.errorMessage(q.getErrorMessage());
                }
                return b.build();
            })
            .toList();
    }

    /**
     * Processes the completion callback from the AI engine.
     * Saves the report, trace logs, and updates the query status.
     */
    @Transactional
    public void completeJob(UUID jobId, AiCompletionCallback callback) {
        Query query = queryRepository.findById(jobId)
                .orElseThrow(() -> new EntityNotFoundException("Job not found: " + jobId));

        // Save the research report
        ResearchReport report = ResearchReport.builder()
                .query(query)
                .executiveSummary(callback.getExecutiveSummary())
                .detailedContent(callback.getDetailedContent())
                .confidenceScore(callback.getConfidenceScore())
                .citations(callback.getCitations())
                .iterationCount(callback.getIterationCount())
                .processingTimeMs(callback.getProcessingTimeMs())
                .build();
        reportRepository.save(report);

        // Save agent trace logs if provided
        if (callback.getTraces() != null && !callback.getTraces().isEmpty()) {
            for (AiCompletionCallback.TraceEntry entry : callback.getTraces()) {
                AgentTrace trace = AgentTrace.builder()
                        .query(query)
                        .iterationNumber(entry.getIterationNumber())
                        .actionTaken(entry.getActionTaken())
                        .actionInput(entry.getActionInput())
                        .observation(entry.getObservation())
                        .build();
                traceRepository.save(trace);
            }
        }

        // Update query status
        query.setStatus("completed");
        queryRepository.save(query);

        // Cache the result in Redis for 24 hours
        String cacheKey = "query_cache:" + hashPrompt(query.getRawPrompt());
        redisTemplate.opsForValue().set(cacheKey, jobId.toString(), Duration.ofHours(24));

        log.info("Job [{}] completed — confidence: {}%, iterations: {}",
                jobId, callback.getConfidenceScore(), callback.getIterationCount());
    }

    private String hashPrompt(String prompt) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] encodedhash = digest.digest(prompt.toLowerCase().trim().getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder(2 * encodedhash.length);
            for (byte b : encodedhash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 not available", e);
        }
    }

    /**
     * Marks a job as failed.
     */
    @Transactional
    public void failJob(UUID jobId, String errorMessage) {
        Query query = queryRepository.findById(jobId)
                .orElseThrow(() -> new EntityNotFoundException("Job not found: " + jobId));

        query.setStatus("failed");
        query.setErrorMessage(errorMessage);
        queryRepository.save(query);

        log.error("Job [{}] failed: {}", jobId, errorMessage);
    }
}
