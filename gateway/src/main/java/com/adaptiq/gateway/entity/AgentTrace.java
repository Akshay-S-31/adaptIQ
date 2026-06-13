package com.adaptiq.gateway.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * Stores telemetry from the AI engine's ReAct/Reflexion loop.
 * Each trace records a single action within an iteration (e.g., FOUNDRY_SEARCH, SELF_CRITIQUE).
 * Invaluable for debugging and understanding the agent's reasoning path.
 */
@Entity
@Table(name = "agent_traces")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AgentTrace {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "query_id")
    private Query query;

    @Column(name = "iteration_number", nullable = false)
    private Integer iterationNumber;

    @Column(name = "action_taken", length = 100)
    private String actionTaken;

    @Column(name = "action_input", columnDefinition = "TEXT")
    private String actionInput;

    @Column(columnDefinition = "TEXT")
    private String observation;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private OffsetDateTime createdAt;
}
