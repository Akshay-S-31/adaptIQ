"""
AdaptIQ — Foundry IQ Knowledge Base

Simulates Microsoft Foundry IQ knowledge retrieval grounded in
enterprise learning content: certification guides, training docs,
and approved learning resources.
"""

import logging
from app.models.schemas import RetrievedDocument

logger = logging.getLogger(__name__)

# ─── Enterprise Learning Knowledge Base ────────────────────────────
# Covers: Azure certification tracks, study strategies, and role mappings.
# IDs use FIQ- prefix (Foundry IQ format).

_KNOWLEDGE_BASE: list[dict] = [

    # ── AZ-204: Developing Solutions for Microsoft Azure ──
    {
        "foundry_id": "FIQ-CERT-AZ204-001",
        "source_url": "https://foundryiq.adaptiq.internal/certs/az-204/overview",
        "snippet": (
            "AZ-204: Developing Solutions for Microsoft Azure is targeted at Cloud Engineers "
            "and developers who design, build, and maintain cloud solutions. Core skills include: "
            "Azure Functions (serverless), Azure App Service, Azure Blob & Cosmos DB storage, "
            "API Management, and Azure Key Vault. Recommended study hours: 20-25. "
            "Target practice score before exam: 75%."
        ),
        "keywords": ["AZ-204", "azure developer", "cloud engineer", "functions", "app service", "cosmos", "storage"],
    },
    {
        "foundry_id": "FIQ-CERT-AZ204-002",
        "source_url": "https://foundryiq.adaptiq.internal/certs/az-204/study-guide",
        "snippet": (
            "AZ-204 Study Guide — Key Domains: (1) Develop Azure compute solutions (25-30%): "
            "containers, functions, VMs; (2) Develop for Azure storage (15-20%): blob, table, Cosmos DB; "
            "(3) Implement Azure security (20-25%): Key Vault, managed identity, OAuth; "
            "(4) Monitor, troubleshoot, optimize (15-20%): Application Insights, caching; "
            "(5) Connect and consume Azure services (15-20%): API Management, Event Grid, Service Bus."
        ),
        "keywords": ["AZ-204", "study guide", "compute", "storage", "security", "monitoring", "domains"],
    },

    # ── AZ-400: Designing and Implementing Microsoft DevOps Solutions ──
    {
        "foundry_id": "FIQ-CERT-AZ400-001",
        "source_url": "https://foundryiq.adaptiq.internal/certs/az-400/overview",
        "snippet": (
            "AZ-400: DevOps Engineer Expert is recommended for DevOps Engineers and SREs. "
            "Core competencies: CI/CD pipeline design (Azure Pipelines, GitHub Actions), "
            "infrastructure as code (Bicep, Terraform), container orchestration (AKS), "
            "monitoring and observability (Azure Monitor), and security in DevOps (DevSecOps). "
            "Prerequisite: AZ-104 or AZ-204. Recommended study hours: 25-30."
        ),
        "keywords": ["AZ-400", "devops", "CI/CD", "pipelines", "GitHub Actions", "IaC", "kubernetes", "AKS"],
    },
    {
        "foundry_id": "FIQ-CERT-AZ400-002",
        "source_url": "https://foundryiq.adaptiq.internal/certs/az-400/study-guide",
        "snippet": (
            "AZ-400 Study Guide — Key Domains: (1) Design and implement source control (15-20%); "
            "(2) Design and implement build and release pipelines (40-45%): multi-stage pipelines, "
            "deployment strategies (blue-green, canary); (3) Implement security and compliance (10-15%); "
            "(4) Implement instrumentation (10-15%): distributed tracing, dashboards; "
            "(5) Design a DevOps strategy (20-25%): team topology, value stream mapping."
        ),
        "keywords": ["AZ-400", "study guide", "pipelines", "deployment", "security", "instrumentation", "devops strategy"],
    },

    # ── DP-203: Data Engineering on Microsoft Azure ──
    {
        "foundry_id": "FIQ-CERT-DP203-001",
        "source_url": "https://foundryiq.adaptiq.internal/certs/dp-203/overview",
        "snippet": (
            "DP-203: Data Engineering on Microsoft Azure targets Data Engineers working with "
            "large-scale data solutions. Core skills: Azure Data Factory (ETL pipelines), "
            "Azure Synapse Analytics (data warehousing), Azure Databricks (Spark-based processing), "
            "Azure Data Lake Storage Gen2, and real-time streaming with Azure Stream Analytics. "
            "Recommended study hours: 20-25."
        ),
        "keywords": ["DP-203", "data engineer", "data factory", "synapse", "databricks", "spark", "data lake", "streaming"],
    },

    # ── AZ-104: Microsoft Azure Administrator ──
    {
        "foundry_id": "FIQ-CERT-AZ104-001",
        "source_url": "https://foundryiq.adaptiq.internal/certs/az-104/overview",
        "snippet": (
            "AZ-104: Microsoft Azure Administrator is the foundational certification for Cloud/IT Administrators. "
            "Covers: Azure identity (Entra ID, RBAC), governance (policies, blueprints), "
            "virtual networking (VNet, NSG, VPN Gateway), compute (VMs, scale sets, AKS basics), "
            "storage (blob, file, backup), and monitoring (Azure Monitor, alerts). "
            "Recommended as a prerequisite to AZ-204 and AZ-400. Study hours: 15-20."
        ),
        "keywords": ["AZ-104", "administrator", "identity", "RBAC", "networking", "VNet", "storage", "governance"],
    },

    # ── Role-to-Certification Mapping ──
    {
        "foundry_id": "FIQ-ROLE-MAP-001",
        "source_url": "https://foundryiq.adaptiq.internal/guides/role-certification-mapping",
        "snippet": (
            "Enterprise Role-to-Certification Mapping:\n"
            "- Cloud Engineer: Primary: AZ-204, Secondary: AZ-305 (Solutions Architect)\n"
            "- DevOps Engineer: Primary: AZ-400, Prerequisite: AZ-104\n"
            "- Data Engineer: Primary: DP-203, Secondary: DP-300\n"
            "- IT Administrator: Primary: AZ-104, Secondary: AZ-500 (Security)\n"
            "- Security Engineer: Primary: AZ-500, Prerequisite: AZ-104\n"
            "- Solutions Architect: Primary: AZ-305, Prerequisite: AZ-104 or AZ-204"
        ),
        "keywords": ["role", "certification", "mapping", "cloud engineer", "devops", "data engineer", "administrator", "architect"],
    },

    # ── Study Best Practices ──
    {
        "foundry_id": "FIQ-GUIDE-STUDY-001",
        "source_url": "https://foundryiq.adaptiq.internal/guides/study-best-practices",
        "snippet": (
            "Engineering Certification Study Best Practices:\n"
            "- Daily focused study: 1-2 hours per day is more effective than weekend cramming.\n"
            "- Weekly checkpoint assessments: target 75%+ practice score before booking the exam.\n"
            "- Use hands-on labs (Microsoft Learn Sandbox) for 30% of study time.\n"
            "- Learners with 20+ study hours and 75%+ practice scores show 68% higher pass rates.\n"
            "- Avoid scheduling exam during high-meeting weeks (>20 meeting hours/week)."
        ),
        "keywords": ["study", "best practices", "tips", "schedule", "exam", "pass rate", "practice score", "labs"],
    },
    {
        "foundry_id": "FIQ-GUIDE-STUDY-002",
        "source_url": "https://foundryiq.adaptiq.internal/guides/study-schedule-template",
        "snippet": (
            "Recommended Study Schedule Template:\n"
            "Week 1-2: Domain overview and architecture concepts (30% of study time)\n"
            "Week 3-4: Hands-on labs and service exploration (40% of study time)\n"
            "Week 5: Practice exams and gap analysis (20% of study time)\n"
            "Week 6: Review weak areas identified in practice exams (10% of study time)\n"
            "Milestone: Score 75%+ on two consecutive practice exams before booking."
        ),
        "keywords": ["schedule", "weekly plan", "template", "milestone", "practice exam", "weeks", "timeline"],
    },

    # ── Team Learning Insights ──
    {
        "foundry_id": "FIQ-REPORT-TEAM-001",
        "source_url": "https://foundryiq.adaptiq.internal/reports/quarterly-learning-q2-2026",
        "snippet": (
            "Quarterly Learning Performance Summary Q2-2026:\n"
            "- Average study time across certified learners: 21 hours\n"
            "- Overall team pass rate: 68%\n"
            "- Top performing role: DevOps Engineers (74% pass rate)\n"
            "- At-risk group: Cloud Engineers with <15 study hours (42% pass rate)\n"
            "- Key insight: Learners who completed all Microsoft Learn modules passed at 81% rate."
        ),
        "keywords": ["team", "report", "pass rate", "performance", "quarterly", "analytics", "at-risk", "insights"],
    },

    # ── Assessment Questions — AZ-204 ──
    {
        "foundry_id": "FIQ-ASSESS-AZ204-001",
        "source_url": "https://foundryiq.adaptiq.internal/assessments/az-204/sample-questions",
        "snippet": (
            "AZ-204 Sample Assessment Questions:\n"
            "Q1: A developer needs to run background processing jobs with no persistent server. "
            "Which Azure service is most appropriate? A: Azure Functions (serverless)\n"
            "Q2: Your app needs to store semi-structured documents with low-latency global reads. "
            "Which service should you choose? A: Azure Cosmos DB\n"
            "Q3: You need to expose your API with usage quotas and developer portal. "
            "Which Azure service handles this? A: Azure API Management\n"
            "Q4: An app must access secrets without storing credentials in code. "
            "What is the recommended pattern? A: Managed Identity + Azure Key Vault"
        ),
        "keywords": ["AZ-204", "assessment", "questions", "quiz", "practice", "functions", "cosmos", "API management", "key vault"],
    },
    {
        "foundry_id": "FIQ-ASSESS-AZ400-001",
        "source_url": "https://foundryiq.adaptiq.internal/assessments/az-400/sample-questions",
        "snippet": (
            "AZ-400 Sample Assessment Questions:\n"
            "Q1: Your team needs zero-downtime deployments with instant rollback. "
            "Which deployment strategy is best? A: Blue-green deployment\n"
            "Q2: You want to gradually shift 10% of traffic to a new version to test stability. "
            "Which strategy applies? A: Canary deployment\n"
            "Q3: Infrastructure changes must be version-controlled and repeatable. "
            "Which approach should you use? A: Infrastructure as Code (Bicep/Terraform)\n"
            "Q4: Your pipeline needs to scan container images for vulnerabilities before deployment. "
            "What is this practice called? A: DevSecOps / Shift-left security"
        ),
        "keywords": ["AZ-400", "assessment", "questions", "quiz", "blue-green", "canary", "IaC", "devsecops"],
    },
]


def _compute_relevance(query: str, keywords: list[str]) -> float:
    """Keyword-matching relevance score."""
    query_lower = query.lower()
    matches = sum(1 for kw in keywords if kw.lower() in query_lower)
    return min(1.0, matches / max(len(keywords) * 0.25, 1))


async def search(query: str, top_k: int = 5) -> list[RetrievedDocument]:
    """
    Search the Foundry IQ enterprise learning knowledge base.

    This is the interface contract — swap this function body with
    real Azure AI Search / Foundry IQ API calls when credentials are available.
    """
    logger.info(f"Foundry IQ search: '{query[:80]}...' (top_k={top_k})")

    scored = []
    for doc in _KNOWLEDGE_BASE:
        score = _compute_relevance(query, doc["keywords"])
        if score > 0.05:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, doc in scored[:top_k]:
        results.append(RetrievedDocument(
            source_url=doc["source_url"],
            snippet=doc["snippet"],
            foundry_id=doc["foundry_id"],
            relevance_score=round(score, 3),
        ))

    logger.info(f"Foundry IQ returned {len(results)} documents")
    return results
