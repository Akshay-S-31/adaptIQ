package com.adaptiq.gateway.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.math.BigDecimal;
import java.util.List;

/**
 * Payload sent by the FastAPI AI engine when a research job completes.
 * This is the callback contract for PUT /internal/jobs/{jobId}/complete
 */
@Data
public class AiCompletionCallback {

    @NotBlank(message = "Executive summary is required")
    private String executiveSummary;

    @NotBlank(message = "Detailed content is required")
    private String detailedContent;

    @NotNull(message = "Confidence score is required")
    private BigDecimal confidenceScore;

    /** JSON-serialized array of citation objects */
    private String citations;

    private Integer iterationCount;
    private Long processingTimeMs;

    /** Optional trace logs from the Reflexion loop */
    private List<TraceEntry> traces;

    @Data
    public static class TraceEntry {
        private Integer iterationNumber;
        private String actionTaken;
        private String actionInput;
        private String observation;
    }
}
