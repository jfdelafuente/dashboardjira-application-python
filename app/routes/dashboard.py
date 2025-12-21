"""
Dashboard blueprint - main page routes.

Handles:
    - GET /: Dashboard home page with KPIs, charts, and issue table
"""

from flask import Blueprint, render_template, flash
from app.services.issue_service import IssueService
from app.services.kpi_service import calculate_kpis

# Create blueprint
bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    """
    Dashboard home page.

    Syncs issues from Jira (or uses mock data), calculates KPIs,
    and renders the dashboard with KPI cards.

    Returns:
        Rendered dashboard.html template with KPI data
    """
    try:
        # Sync issues from Jira (only in development/production, not testing)
        from flask import current_app

        issue_service = IssueService()
        if not current_app.config.get("TESTING", False):
            sync_stats = issue_service.sync_from_jira()
        else:
            sync_stats = {"created": 0, "updated": 0, "errors": 0}

        # Calculate KPIs
        kpis = calculate_kpis()

        # Pass data to template
        return render_template("dashboard.html", kpis=kpis, sync_stats=sync_stats)

    except Exception as e:
        # Handle errors gracefully
        flash(
            f"Error loading dashboard data: {str(e)}. Please try again later.", "error"
        )
        return render_template(
            "dashboard.html",
            kpis={
                "total_open": 0,
                "critical_issues": 0,
                "avg_resolution_time_hours": 0,
                "overdue_tickets": 0,
            },
            sync_stats={"created": 0, "updated": 0, "errors": 1},
        )
