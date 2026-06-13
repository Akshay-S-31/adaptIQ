package com.adaptiq.gateway.controller;

import com.adaptiq.gateway.service.LearningService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.UUID;

/**
 * Manager-only REST controller for team-level learning insights.
 *
 * GET /api/v1/manager/insights         — All-teams insights (Manager Insights Agent)
 * GET /api/v1/manager/insights/{team}  — Single-team insights
 * GET /api/v1/manager/learners         — Fabric IQ learner profiles
 * GET /api/v1/manager/teams            — Fabric IQ team analytics
 *
 * All endpoints require ROLE_MANAGER authority.
 * Learner-role users receive 403 Forbidden.
 */
@RestController
@RequestMapping("/api/v1/manager")
@RequiredArgsConstructor
@Slf4j
@PreAuthorize("hasRole('MANAGER')")
public class ManagerController {

    private final LearningService learningService;

    /**
     * Returns Manager Insights Agent output for all teams.
     */
    @GetMapping("/insights")
    public ResponseEntity<Map<String, Object>> getAllInsights(Authentication authentication) {
        UUID userId = UUID.fromString(authentication.getName());
        log.info("Manager [{}] requested all-teams insights", userId);
        return ResponseEntity.ok(learningService.getManagerInsights(null));
    }

    /**
     * Returns Manager Insights Agent output for a specific team.
     */
    @GetMapping("/insights/{teamId}")
    public ResponseEntity<Map<String, Object>> getTeamInsights(
            @PathVariable String teamId,
            Authentication authentication) {
        UUID userId = UUID.fromString(authentication.getName());
        log.info("Manager [{}] requested insights for team '{}'", userId, teamId);
        return ResponseEntity.ok(learningService.getManagerInsights(teamId));
    }

    /**
     * Returns all Fabric IQ learner profiles (anonymized for demo).
     */
    @GetMapping("/learners")
    public ResponseEntity<Map<String, Object>> getLearners() {
        return ResponseEntity.ok(learningService.getAllLearnerProfiles());
    }

    /**
     * Returns all Fabric IQ team analytics.
     */
    @GetMapping("/teams")
    public ResponseEntity<Map<String, Object>> getTeams() {
        return ResponseEntity.ok(learningService.getAllTeamAnalytics());
    }
}
