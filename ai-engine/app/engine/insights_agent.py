"""
AdaptIQ — Manager Insights Agent

Provides team-level visibility into certification readiness, progress,
and risk areas using Fabric IQ analytics and Work IQ capacity signals.
Surfaces aggregate insights without exposing individual sensitive data.
"""

import logging
from google import genai
from app.config import settings
from app.services.fabric_iq import get_all_team_analytics, get_all_learners, get_certification_ontology
from app.services.work_iq import get_all_team_signals

logger = logging.getLogger(__name__)

INSIGHTS_SYSTEM_PROMPT = """You are the Manager Insights Agent for AdaptIQ, an enterprise learning system.

Your role is to provide team-level visibility into certification readiness and workforce learning health.

Rules:
- Summarize team progress using aggregate metrics (never expose individual private data)
- Highlight at-risk groups and capacity-constrained teams
- Provide actionable recommendations for managers
- Use Fabric IQ analytics data and Work IQ capacity signals
- Be specific with percentages and numbers

Format your response as:
TEAM_OVERVIEW:
<summary of overall team learning health>

READINESS_BY_CERTIFICATION:
<breakdown by cert track>

AT_RISK_GROUPS:
<teams or groups that need attention>

CAPACITY_ANALYSIS:
<Work IQ-based workload assessment>

RECOMMENDATIONS:
<3-5 specific, actionable recommendations for the manager>"""


async def generate_manager_insights(team_id: str = None) -> dict:
    """
    Generate manager-level insights for team learning health.

    Args:
        team_id: Optional specific team (None = all teams)

    Returns:
        dict with insights output and underlying data
    """
    logger.info(f"Manager Insights Agent: generating insights for team='{team_id or 'all'}'")

    # Step 1: Fabric IQ — team analytics
    all_teams = get_all_team_analytics()
    teams_to_analyze = [t for t in all_teams if team_id is None or t["team_id"] == team_id]

    fabric_context = "Fabric IQ — Team Performance Analytics:\n"
    for team in teams_to_analyze:
        fabric_context += f"""
Team: {team['team_name']} ({team['team_id']})
- Average Practice Score: {team['avg_practice_score']}%
- Average Study Hours: {team['avg_hours_studied']}h
- Pass Rate: {int(team['pass_rate'] * 100)}%
- Team Readiness Score: {team['team_readiness_score']}/100
- At-Risk Learners: {len(team['at_risk_learners'])} member(s)
- Certifications In Progress: {', '.join(team['certifications_in_progress'])}
- Capacity Risk: {team['capacity_risk']}
"""

    # Step 2: Work IQ — team capacity signals
    all_work_signals = get_all_team_signals()
    work_signals_to_analyze = [s for s in all_work_signals if team_id is None or s["team_id"] == team_id]

    work_context = "\nWork IQ — Team Capacity Signals:\n"
    for signal in work_signals_to_analyze:
        work_context += f"""
Team: {signal['team_name']} ({signal['team_id']})
- Avg Meeting Hours/Week: {signal['avg_meeting_hours_per_week']}h
- Avg Focus Hours/Week: {signal['avg_focus_hours_per_week']}h
- Best Team Learning Slot: {signal['best_team_learning_slot']}
- Capacity Risk: {signal['capacity_risk']}
"""

    # Step 3: Overall aggregate stats
    all_learners = get_all_learners()
    passed = [l for l in all_learners if l["exam_outcome"] == "Pass"]
    at_risk = [l for l in all_learners if l["readiness_score"] < 50]

    aggregate_context = f"""
Overall Aggregate (Fabric IQ):
- Total Learners Tracked: {len(all_learners)}
- Certifications Passed: {len(passed)}
- Learners at Risk (readiness < 50): {len(at_risk)}
- Overall Pass Rate: {int(len(passed)/len(all_learners)*100)}%
"""

    user_prompt = f"""{fabric_context}
{work_context}
{aggregate_context}

Generate actionable manager insights for {'team ' + team_id if team_id else 'all teams'}."""

    client = genai.Client(api_key=settings.google_api_key)
    response = client.models.generate_content(
        model=settings.llm_model,
        contents=f"{INSIGHTS_SYSTEM_PROMPT}\n\n{user_prompt}",
        config={"temperature": 0.3},
    )

    raw_text = response.text.strip()
    logger.info(f"Manager Insights Agent: generated insights ({len(raw_text)} chars)")

    return {
        "agent": "Manager Insights Agent",
        "scope": team_id or "all_teams",
        "output": raw_text,
        "fabric_iq_summary": {
            "teams_analyzed": len(teams_to_analyze),
            "total_learners": len(all_learners),
            "pass_rate": f"{int(len(passed)/len(all_learners)*100)}%",
            "at_risk_count": len(at_risk),
        },
        "work_iq_summary": {
            "teams_with_high_capacity_risk": len([s for s in work_signals_to_analyze if s["capacity_risk"] == "High"]),
        },
    }
