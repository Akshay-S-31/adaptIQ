package com.adaptiq.gateway.service;

import com.adaptiq.gateway.dto.JobAcceptedResponse;
import com.adaptiq.gateway.dto.JobStatusResponse;
import com.adaptiq.gateway.entity.Query;
import com.adaptiq.gateway.entity.ResearchReport;
import com.adaptiq.gateway.entity.User;
import com.adaptiq.gateway.repository.QueryRepository;
import com.adaptiq.gateway.repository.ResearchReportRepository;
import com.adaptiq.gateway.repository.UserRepository;
import com.adaptiq.gateway.repository.AgentTraceRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Business logic for enterprise learning job management.
 *
 * Handles submission of learning plan and assessment jobs to the AI engine,
 * job status polling, history retrieval, and manager-level data access.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class LearningService {

    private final QueryRepository queryRepository;
    private final ResearchReportRepository reportRepository;
    private final UserRepository userRepository;
    private final AgentTraceRepository agentTraceRepository;
    private final AiEngineClient aiEngineClient;

    /**
     * Submit a learning plan job (Curator + Study Plan agents).
     * The AI engine endpoint is /internal/ai/learn/plan.
     */
    @Transactional
    public UUID submitLearningPlan(
            String role,
            String goal,
            String employeeId,
            String experienceLevel,
            int weeksAvailable,
            UUID userId) {

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new EntityNotFoundException("User not found: " + userId));

        String rawPrompt = String.format("[LEARNING_PLAN] role=%s, goal=%s", role, goal);

        Query query = Query.builder()
                .rawPrompt(rawPrompt)
                .status("processing")
                .user(user)
                .build();
        query = queryRepository.save(query);

        log.info("Created learning plan job [{}] for user [{}]: role={}, goal={}",
                query.getId(), userId, role, goal);

        // Dispatch to the AI Engine's learning endpoint
        aiEngineClient.dispatchLearningPlan(
                query.getId(), role, goal, employeeId, experienceLevel, weeksAvailable);

        return query.getId();
    }

    /**
     * Submit an assessment job (Assessment Agent).
     */
    @Transactional
    public UUID submitAssessment(String targetCertification, String employeeId, UUID userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new EntityNotFoundException("User not found: " + userId));

        String rawPrompt = String.format("[ASSESSMENT] cert=%s, employee=%s",
                targetCertification, employeeId);

        Query query = Query.builder()
                .rawPrompt(rawPrompt)
                .status("processing")
                .user(user)
                .build();
        query = queryRepository.save(query);

        log.info("Created assessment job [{}] for user [{}]: cert={}",
                query.getId(), userId, targetCertification);

        aiEngineClient.dispatchAssessment(query.getId(), targetCertification, employeeId);

        return query.getId();
    }

    /**
     * Get status and result of a specific job.
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
     * Get learning job history for a specific user.
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
                        reportRepository.findByQueryId(q.getId()).ifPresent(r ->
                                b.confidenceScore(r.getConfidenceScore()));
                    } else if ("failed".equals(q.getStatus())) {
                        b.errorMessage(q.getErrorMessage());
                    }
                    return b.build();
                })
                .toList();
    }

    /**
     * Delete a specific job from history.
     */
    @Transactional
    public void deleteJob(UUID jobId, UUID userId) {
        Query query = queryRepository.findById(jobId)
                .orElseThrow(() -> new EntityNotFoundException("Job not found: " + jobId));

        if (!query.getUser().getId().equals(userId)) {
            throw new org.springframework.security.access.AccessDeniedException("Cannot delete someone else's job");
        }

        agentTraceRepository.deleteByQueryId(jobId);
        reportRepository.findByQueryId(jobId).ifPresent(reportRepository::delete);
        queryRepository.delete(query);
    }

    /**
     * Synchronously fetch Manager Insights from the AI Engine.
     * Returned directly (not a background job) for the manager dashboard.
     */
    public Map<String, Object> getManagerInsights(String teamId) {
        return aiEngineClient.fetchManagerInsights(teamId);
    }

    /**
     * Return Fabric IQ learner profiles (for manager dashboard).
     */
    public Map<String, Object> getAllLearnerProfiles() {
        return aiEngineClient.fetchLearnerProfiles();
    }

    /**
     * Return Fabric IQ team analytics (for manager dashboard).
     */
    public Map<String, Object> getAllTeamAnalytics() {
        return aiEngineClient.fetchTeamAnalytics();
    }
}
