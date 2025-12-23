"""
Chart data service.

Provides functions to generate chart data for Chart.js visualizations:
    - get_status_distribution: Status distribution for bar chart
    - get_priority_distribution: Priority distribution for pie chart
"""

from typing import Dict, List
from app.models.issue import Issue


class ChartService:
    """Service for generating chart data."""

    def get_status_distribution(self) -> Dict[str, List]:
        """
        Get status distribution data for bar chart.

        Returns all issues grouped by status (To Do, In Progress, Done).

        Returns:
            dict: Dictionary with keys:
                - labels (list): Status labels
                  ["To Do", "In Progress", "Done"]
                - data (list): Count of issues for each status
        """
        statuses = ["To Do", "In Progress", "Done"]
        counts = []

        for status in statuses:
            count = Issue.query.filter(Issue.status == status).count()
            counts.append(count)

        return {"labels": statuses, "data": counts}

    def get_priority_distribution(self) -> Dict[str, List]:
        """
        Get priority distribution data for pie chart.

        Returns only open issues (status != Done) grouped by priority.

        Returns:
            dict: Dictionary with keys:
                - labels (list): Priority labels
                  ["Critical", "High", "Medium", "Low"]
                - data (list): Count of open issues for each priority
        """
        priorities = ["Critical", "High", "Medium", "Low"]
        counts = []

        for priority in priorities:
            count = Issue.query.filter(
                Issue.priority == priority, Issue.status != "Done"
            ).count()
            counts.append(count)

        return {"labels": priorities, "data": counts}
