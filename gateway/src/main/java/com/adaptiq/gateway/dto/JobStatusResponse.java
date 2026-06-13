package com.adaptiq.gateway.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * Full job status response returned by the polling endpoint.
 * When the job is still processing, report fields will be null.
 * When completed, the full report is included inline.
 */
@Data
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class JobStatusResponse {

    private UUID jobId;
    private String status;
    private String rawPrompt;
    private OffsetDateTime createdAt;

    // --- Populated only when status = "completed" ---
    private String executiveSummary;
    private String detailedContent;
    private BigDecimal confidenceScore;
    private String citations;
    private Integer iterationCount;
    private Long processingTimeMs;

    // --- Populated only when status = "failed" ---
    private String errorMessage;
}
