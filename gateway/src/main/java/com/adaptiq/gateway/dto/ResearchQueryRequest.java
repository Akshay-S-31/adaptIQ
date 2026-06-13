package com.adaptiq.gateway.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * Inbound request from the client to submit a research query.
 */
@Data
public class ResearchQueryRequest {

    @NotBlank(message = "Query text must not be blank")
    @Size(min = 10, max = 5000, message = "Query must be between 10 and 5000 characters")
    private String query;
}
