package com.adaptiq.gateway.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * Represents a registered user of the AdaptIQ Enterprise Learning Platform.
 *
 * Roles:
 *   LEARNER — An employee working towards a certification
 *   MANAGER — A team lead/manager viewing team-level learning insights
 *
 * Role is assigned at registration and embedded into the JWT by the server.
 */
@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(unique = true, nullable = false, length = 255)
    private String email;

    @Column(name = "password_hash", nullable = false)
    private String passwordHash;

    /**
     * The user's display name.
     */
    @Column(name = "full_name", length = 255)
    private String fullName;

    /**
     * LEARNER or MANAGER. Determines which UI and API endpoints are accessible.
     * Defaults to LEARNER on registration.
     */
    @Column(length = 20)
    @Builder.Default
    private String role = "LEARNER";

    /**
     * The Fabric IQ / Work IQ employee ID (e.g., "EMP-1001").
     * Links the user to their learning profile and workplace signals.
     */
    @Column(name = "employee_id", length = 50)
    @Builder.Default
    private String employeeId = "EMP-1001";

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private OffsetDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private OffsetDateTime updatedAt;
}
