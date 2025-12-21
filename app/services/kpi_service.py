"""
KPI calculation service.

Provides functions to calculate Key Performance Indicators for the support dashboard:
    - total_open: Count of open issues (status != Done)
    - critical_issues: Count of open critical priority issues
    - avg_resolution_time_hours: Average hours from creation to resolution
    - overdue_tickets: Count of issues past SLA deadline and not resolved
"""

from datetime import datetime
from typing import Dict
from app.models.issue import Issue


def calculate_kpis() -> Dict[str, float]:
    """
    Calculate all KPI metrics for the dashboard.

    Returns:
        dict: Dictionary containing all 4 KPI values:
            - total_open (int): Count of issues where status != 'Done'
            - critical_issues (int): Count of Critical priority issues
              where status != 'Done'
            - avg_resolution_time_hours (float): Average resolution time
              in hours (0 if no resolved issues)
            - overdue_tickets (int): Count of issues past SLA deadline
              and not resolved
    """
    # Calculate total open issues
    total_open = Issue.query.filter(Issue.status != "Done").count()

    # Calculate critical issues (Critical priority AND not Done)
    critical_issues = Issue.query.filter(
        Issue.priority == "Critical", Issue.status != "Done"
    ).count()

    # Calculate average resolution time
    resolved_issues = (
        Issue.query.filter(Issue.resolved_at.isnot(None))
        .with_entities(Issue.created_at, Issue.resolved_at)
        .all()
    )

    if resolved_issues:
        total_hours = sum(
            (resolved - created).total_seconds() / 3600
            for created, resolved in resolved_issues
        )
        avg_resolution_time_hours = total_hours / len(resolved_issues)
    else:
        avg_resolution_time_hours = 0

    # Calculate overdue tickets (SLA deadline passed AND not resolved)
    now = datetime.utcnow()
    overdue_tickets = Issue.query.filter(
        Issue.sla_deadline.isnot(None),
        Issue.sla_deadline < now,
        Issue.status != "Done",
    ).count()

    return {
        "total_open": total_open,
        "critical_issues": critical_issues,
        "avg_resolution_time_hours": avg_resolution_time_hours,
        "overdue_tickets": overdue_tickets,
    }
