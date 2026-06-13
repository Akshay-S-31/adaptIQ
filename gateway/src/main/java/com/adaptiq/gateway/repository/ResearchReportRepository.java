package com.adaptiq.gateway.repository;

import com.adaptiq.gateway.entity.ResearchReport;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface ResearchReportRepository extends JpaRepository<ResearchReport, UUID> {
    Optional<ResearchReport> findByQueryId(UUID queryId);
}
