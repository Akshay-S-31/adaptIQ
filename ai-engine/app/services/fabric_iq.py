"""
AdaptIQ — Fabric IQ Simulation Layer

Simulates Microsoft Fabric IQ — the semantic intelligence layer that
models learner performance, skill gaps, readiness scores, and
structured certification data with business-level relationships.
"""

from typing import Optional

# ─── Learner Performance Data ─────────────────────────────────────

_LEARNER_DATA: list[dict] = [
    {
        "learner_id": "L-1001",
        "employee_id": "EMP-1001",
        "role": "Cloud Engineer",
        "target_certification": "AZ-204",
        "practice_score_avg": 67,
        "hours_studied": 18,
        "modules_completed": 7,
        "total_modules": 12,
        "exam_outcome": None,  # Not yet attempted
        "readiness_score": 58,  # Fabric IQ computed semantic score
        "skill_gaps": ["Azure Functions advanced patterns", "Cosmos DB consistency levels"],
        "strengths": ["Azure App Service", "Key Vault integration"],
        "study_start_date": "2026-05-01",
        "predicted_pass_probability": 0.55,
    },
    {
        "learner_id": "L-1002",
        "employee_id": "EMP-1002",
        "role": "DevOps Engineer",
        "target_certification": "AZ-400",
        "practice_score_avg": 82,
        "hours_studied": 24,
        "modules_completed": 14,
        "total_modules": 16,
        "exam_outcome": "Pass",
        "readiness_score": 84,
        "skill_gaps": [],
        "strengths": ["CI/CD pipelines", "Deployment strategies", "GitHub Actions"],
        "study_start_date": "2026-04-10",
        "predicted_pass_probability": 0.89,
    },
    {
        "learner_id": "L-1003",
        "employee_id": "EMP-1003",
        "role": "Data Engineer",
        "target_certification": "DP-203",
        "practice_score_avg": 74,
        "hours_studied": 20,
        "modules_completed": 10,
        "total_modules": 14,
        "exam_outcome": "Pass",
        "readiness_score": 76,
        "skill_gaps": ["Azure Stream Analytics windowing functions"],
        "strengths": ["Azure Data Factory", "Databricks", "Data Lake Gen2"],
        "study_start_date": "2026-04-20",
        "predicted_pass_probability": 0.75,
    },
    {
        "learner_id": "L-1004",
        "employee_id": "EMP-1004",
        "role": "Cloud Engineer",
        "target_certification": "AZ-204",
        "practice_score_avg": 51,
        "hours_studied": 8,
        "modules_completed": 3,
        "total_modules": 12,
        "exam_outcome": None,
        "readiness_score": 32,
        "skill_gaps": ["Azure Functions", "API Management", "Cosmos DB", "Security patterns"],
        "strengths": ["Azure App Service basics"],
        "study_start_date": "2026-05-15",
        "predicted_pass_probability": 0.28,
    },
    {
        "learner_id": "L-1005",
        "employee_id": "EMP-1005",
        "role": "DevOps Engineer",
        "target_certification": "AZ-400",
        "practice_score_avg": 71,
        "hours_studied": 17,
        "modules_completed": 9,
        "total_modules": 16,
        "exam_outcome": None,
        "readiness_score": 65,
        "skill_gaps": ["Blue-green deployment strategy", "Value stream mapping"],
        "strengths": ["GitHub Actions", "Azure Monitor", "Bicep IaC"],
        "study_start_date": "2026-05-05",
        "predicted_pass_probability": 0.63,
    },
]

# ─── Certification Semantic Model (Fabric IQ Ontology) ───────────────────────

_CERTIFICATION_ONTOLOGY: dict[str, dict] = {
    "AZ-104": {
        "id": "AZ-104",
        "name": "Microsoft Azure Administrator",
        "skills": ["Identity & RBAC", "Networking", "Storage", "Compute", "Monitoring"],
        "recommended_hours": 18,
        "pass_threshold_score": 75,
        "difficulty": "Intermediate",
        "prerequisites": [],
        "target_roles": ["IT Administrator", "Cloud Administrator"],
    },
    "AZ-204": {
        "id": "AZ-204",
        "name": "Developing Solutions for Microsoft Azure",
        "skills": ["Azure Functions", "App Service", "Cosmos DB", "API Management", "Key Vault"],
        "recommended_hours": 22,
        "pass_threshold_score": 75,
        "difficulty": "Intermediate",
        "prerequisites": ["AZ-104"],
        "target_roles": ["Cloud Engineer", "Software Developer"],
    },
    "AZ-400": {
        "id": "AZ-400",
        "name": "Designing and Implementing DevOps Solutions",
        "skills": ["CI/CD Pipelines", "GitHub Actions", "IaC", "AKS", "Monitoring"],
        "recommended_hours": 28,
        "pass_threshold_score": 75,
        "difficulty": "Advanced",
        "prerequisites": ["AZ-104", "AZ-204"],
        "target_roles": ["DevOps Engineer", "SRE", "Platform Engineer"],
    },
    "DP-203": {
        "id": "DP-203",
        "name": "Data Engineering on Microsoft Azure",
        "skills": ["Data Factory", "Synapse Analytics", "Databricks", "Stream Analytics", "Data Lake"],
        "recommended_hours": 24,
        "pass_threshold_score": 75,
        "difficulty": "Intermediate",
        "prerequisites": ["AZ-104"],
        "target_roles": ["Data Engineer", "Analytics Engineer"],
    },
}

# ─── Team Performance Analytics ──────────────────────────────────────────────

_TEAM_ANALYTICS: dict[str, dict] = {
    "TEAM-A": {
        "team_id": "TEAM-A",
        "team_name": "Cloud Platform Team",
        "members": ["L-1001", "L-1003"],
        "avg_practice_score": 70.5,
        "avg_hours_studied": 19.0,
        "pass_rate": 0.50,
        "at_risk_learners": ["L-1001"],
        "certifications_in_progress": ["AZ-204", "DP-203"],
        "team_readiness_score": 67,
        "capacity_risk": "Medium",
    },
    "TEAM-B": {
        "team_id": "TEAM-B",
        "team_name": "DevOps & Infrastructure Team",
        "members": ["L-1002", "L-1004", "L-1005"],
        "avg_practice_score": 68.0,
        "avg_hours_studied": 16.3,
        "pass_rate": 0.33,
        "at_risk_learners": ["L-1004"],
        "certifications_in_progress": ["AZ-400", "AZ-204"],
        "team_readiness_score": 60,
        "capacity_risk": "High",
    },
}


def get_learner_profile(learner_id: str) -> Optional[dict]:
    """Get Fabric IQ learner profile by ID."""
    for l in _LEARNER_DATA:
        if l["learner_id"] == learner_id:
            return l
    return None


def get_learner_by_employee(employee_id: str) -> Optional[dict]:
    """Get Fabric IQ learner profile by employee ID."""
    for l in _LEARNER_DATA:
        if l["employee_id"] == employee_id:
            return l
    return None


def get_certification_ontology(cert_id: str) -> Optional[dict]:
    """Get certification semantic model."""
    return _CERTIFICATION_ONTOLOGY.get(cert_id.upper())


def get_team_analytics(team_id: str) -> Optional[dict]:
    """Get team-level performance analytics."""
    return _TEAM_ANALYTICS.get(team_id)


def get_all_learners() -> list[dict]:
    """Return all learner profiles."""
    return _LEARNER_DATA


def get_all_team_analytics() -> list[dict]:
    """Return all team analytics."""
    return list(_TEAM_ANALYTICS.values())


def compute_readiness_gap(learner_id: str) -> dict:
    """
    Fabric IQ semantic reasoning: compute the gap between
    current readiness and the certification pass threshold.
    """
    learner = get_learner_profile(learner_id)
    if not learner:
        return {"error": f"Learner {learner_id} not found"}

    cert = get_certification_ontology(learner["target_certification"])
    threshold = cert["pass_threshold_score"] if cert else 75

    gap = threshold - learner["readiness_score"]
    hours_needed = max(0, (cert["recommended_hours"] if cert else 20) - learner["hours_studied"])

    return {
        "learner_id": learner_id,
        "target_certification": learner["target_certification"],
        "current_readiness": learner["readiness_score"],
        "pass_threshold": threshold,
        "readiness_gap": gap,
        "estimated_hours_remaining": hours_needed,
        "skill_gaps": learner["skill_gaps"],
        "predicted_pass_probability": learner["predicted_pass_probability"],
        "recommendation": (
            "On track — continue current study plan." if gap <= 10
            else f"Needs {hours_needed} more study hours. Focus on: {', '.join(learner['skill_gaps'][:2])}."
        ),
    }
