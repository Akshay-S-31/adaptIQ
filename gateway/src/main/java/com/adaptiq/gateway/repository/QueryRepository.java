package com.adaptiq.gateway.repository;

import com.adaptiq.gateway.entity.Query;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface QueryRepository extends JpaRepository<Query, UUID> {
    List<Query> findByUserIdOrderByCreatedAtDesc(UUID userId);
}
