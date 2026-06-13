package com.adaptiq.gateway.repository;

import com.adaptiq.gateway.entity.AgentTrace;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface AgentTraceRepository extends JpaRepository<AgentTrace, UUID> {
    List<AgentTrace> findByQueryIdOrderByIterationNumberAsc(UUID queryId);
    void deleteByQueryId(UUID queryId);
}
