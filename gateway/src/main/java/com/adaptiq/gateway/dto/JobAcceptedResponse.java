package com.adaptiq.gateway.dto;

import lombok.Builder;
import lombok.Data;

import java.util.UUID;

/**
 * Response returned when a research query is accepted (202 Accepted).
 */
@Data
@Builder
public class JobAcceptedResponse {

    private UUID jobId;
    private String status;
    private String message;
}
