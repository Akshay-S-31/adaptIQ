package com.adaptiq.gateway.controller;

import com.adaptiq.gateway.dto.JobStatusResponse;
import com.adaptiq.gateway.service.ResearchService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import java.util.UUID;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class ResearchControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ResearchService researchService;

    @Test
    void shouldRejectUnauthenticatedRequest() throws Exception {
        mockMvc.perform(post("/api/v1/research/query")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"query\": \"Test query\"}"))
                .andExpect(status().isForbidden()); // or isUnauthorized depending on exact config
    }

    @Test
    @WithMockUser(username = "user1", authorities = {"ROLE_STANDARD"})
    void shouldAcceptAuthenticatedRequest() throws Exception {
        UUID mockJobId = UUID.randomUUID();
        when(researchService.submitQuery(anyString(), org.mockito.ArgumentMatchers.any(UUID.class))).thenReturn(mockJobId);

        mockMvc.perform(post("/api/v1/research/query")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"query\": \"Test query\"}"))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.jobId").value(mockJobId.toString()));
    }

    @Test
    @WithMockUser(username = "user1", authorities = {"ROLE_STANDARD"})
    void shouldReturnJobStatus() throws Exception {
        UUID mockJobId = UUID.randomUUID();
        JobStatusResponse mockResponse = JobStatusResponse.builder()
                .jobId(mockJobId)
                .status("processing")
                .build();

        when(researchService.getJobStatus(mockJobId)).thenReturn(mockResponse);

        mockMvc.perform(get("/api/v1/research/jobs/" + mockJobId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("processing"));
    }
}
