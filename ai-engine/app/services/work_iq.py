"""
AdaptIQ — Work IQ Simulation Layer

Simulates Microsoft Work IQ — the intelligence layer that provides
workplace context signals: meeting load, focus time, collaboration patterns,
and preferred learning windows.
"""

from typing import Optional

# ─── Employee Work Signal Data ────────────────────────────────────

_WORK_SIGNALS: dict[str, dict] = {
    "EMP-1001": {
        "employee_id": "EMP-1001",
        "meeting_hours_per_week": 22,
        "focus_hours_per_week": 10,
        "preferred_learning_slot": "Morning (9–11 AM)",
        "avg_daily_focus_blocks": 2,
        "peak_collaboration_day": "Tuesday",
        "low_meeting_day": "Friday",
        "current_workload": "High",
        "notes": "Heavy meeting schedule — recommend short 45-min study blocks on Friday afternoons",
    },
    "EMP-1002": {
        "employee_id": "EMP-1002",
        "meeting_hours_per_week": 15,
        "focus_hours_per_week": 18,
        "preferred_learning_slot": "Afternoon (2–4 PM)",
        "avg_daily_focus_blocks": 3,
        "peak_collaboration_day": "Wednesday",
        "low_meeting_day": "Monday",
        "current_workload": "Medium",
        "notes": "Good focus time availability — suitable for 90-min deep study sessions",
    },
    "EMP-1003": {
        "employee_id": "EMP-1003",
        "meeting_hours_per_week": 8,
        "focus_hours_per_week": 24,
        "preferred_learning_slot": "Morning (8–10 AM)",
        "avg_daily_focus_blocks": 4,
        "peak_collaboration_day": "Thursday",
        "low_meeting_day": "Tuesday",
        "current_workload": "Low",
        "notes": "Excellent focus availability — can sustain 2-hour daily study sessions",
    },
    "EMP-1004": {
        "employee_id": "EMP-1004",
        "meeting_hours_per_week": 28,
        "focus_hours_per_week": 6,
        "preferred_learning_slot": "Evening (6–8 PM)",
        "avg_daily_focus_blocks": 1,
        "peak_collaboration_day": "Monday",
        "low_meeting_day": "Friday",
        "current_workload": "Very High",
        "notes": "Very constrained schedule — recommend pausing certification until workload reduces",
    },
    "EMP-1005": {
        "employee_id": "EMP-1005",
        "meeting_hours_per_week": 12,
        "focus_hours_per_week": 20,
        "preferred_learning_slot": "Morning (9–11 AM)",
        "avg_daily_focus_blocks": 3,
        "peak_collaboration_day": "Wednesday",
        "low_meeting_day": "Thursday",
        "current_workload": "Medium",
        "notes": "Good balance — standard 6-week certification plan is recommended",
    },
}

# Team-level work signal aggregates
_TEAM_SIGNALS: dict[str, dict] = {
    "TEAM-A": {
        "team_id": "TEAM-A",
        "team_name": "Cloud Platform Team",
        "avg_meeting_hours_per_week": 18.5,
        "avg_focus_hours_per_week": 14.2,
        "members": ["EMP-1001", "EMP-1002", "EMP-1003"],
        "best_team_learning_slot": "Friday Morning",
        "capacity_risk": "Medium",
    },
    "TEAM-B": {
        "team_id": "TEAM-B",
        "team_name": "DevOps & Infrastructure Team",
        "avg_meeting_hours_per_week": 20.0,
        "avg_focus_hours_per_week": 13.0,
        "members": ["EMP-1004", "EMP-1005"],
        "best_team_learning_slot": "Thursday Afternoon",
        "capacity_risk": "High",
    },
}


def get_employee_signals(employee_id: str) -> Optional[dict]:
    """Get work signals for a specific employee."""
    return _WORK_SIGNALS.get(employee_id)


def get_team_signals(team_id: str) -> Optional[dict]:
    """Get aggregate work signals for a team."""
    return _TEAM_SIGNALS.get(team_id)


def get_all_employee_signals() -> list[dict]:
    """Return all employee signals."""
    return list(_WORK_SIGNALS.values())


def get_all_team_signals() -> list[dict]:
    """Return all team signals."""
    return list(_TEAM_SIGNALS.values())


def recommend_study_slots(employee_id: str) -> dict:
    """
    Generate study slot recommendations based on Work IQ signals.
    This is the Work IQ intelligence layer in action.
    """
    signals = get_employee_signals(employee_id)
    if not signals:
        return {
            "employee_id": employee_id,
            "recommendation": "No work signal data available. Using default: 1 hour daily, morning slot.",
            "suggested_daily_hours": 1.0,
            "suggested_slot": "Morning",
            "risk_level": "Unknown",
        }

    weekly_focus = signals["focus_hours_per_week"]
    weekly_meetings = signals["meeting_hours_per_week"]
    workload = signals["current_workload"]

    # Work IQ reasoning logic
    if weekly_meetings > 25:
        daily_hours = 0.5
        risk = "High"
        rec = f"Very limited study time due to {weekly_meetings}h/week meeting load. Recommend 30-min micro-sessions on {signals['low_meeting_day']}."
    elif weekly_focus >= 20:
        daily_hours = 1.5
        risk = "Low"
        rec = f"Good focus availability ({weekly_focus}h/week). Recommended 90-min sessions in {signals['preferred_learning_slot']}."
    elif weekly_focus >= 12:
        daily_hours = 1.0
        risk = "Medium"
        rec = f"Moderate focus time ({weekly_focus}h/week). Recommended 60-min sessions in {signals['preferred_learning_slot']}."
    else:
        daily_hours = 0.5
        risk = "High"
        rec = f"Low focus availability ({weekly_focus}h/week). Consider adjusting workload before starting certification."

    return {
        "employee_id": employee_id,
        "recommendation": rec,
        "suggested_daily_hours": daily_hours,
        "suggested_slot": signals["preferred_learning_slot"],
        "low_meeting_day": signals["low_meeting_day"],
        "risk_level": risk,
        "notes": signals["notes"],
    }
