"""
API blueprint - JSON endpoints.

Handles:
    - GET /api/kpis: KPI metrics
    - GET /api/issues: Paginated issues with filtering
    - GET /api/charts/status: Status distribution data
    - GET /api/charts/priority: Priority distribution data
"""

from flask import Blueprint, jsonify, request
from app.services.kpi_service import calculate_kpis
from app.services.chart_service import ChartService
from app.services.issue_service import IssueService

# Create blueprint
bp = Blueprint("api", __name__)


@bp.route("/kpis")
def get_kpis():
    """
    Get KPI metrics.

    Returns:
        JSON response with KPI data
    """
    kpis = calculate_kpis()
    return jsonify(kpis)


@bp.route("/issues")
def get_issues():
    """
    Get paginated issues with optional filtering.

    Query Parameters:
        search: Text search query
        priority: Filter by priority
        page: Page number (default: 1)
        per_page: Items per page (default: 50)

    Returns:
        JSON response with issues and pagination info
    """
    # Get query parameters
    search = request.args.get("search")
    priority = request.args.get("priority")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    # Get filtered and paginated issues
    issue_service = IssueService()
    result = issue_service.get_paginated_issues(
        search=search, priority=priority, page=page, per_page=per_page
    )

    # Convert issues to JSON-serializable format
    issues_json = []
    for issue in result["issues"]:
        issue_dict = {
            "id": issue.id,
            "jira_key": issue.jira_key,
            "summary": issue.summary,
            "status": issue.status,
            "priority": issue.priority,
            "assignee_name": issue.assignee.name if issue.assignee else None,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
        }
        issues_json.append(issue_dict)

    return jsonify({"issues": issues_json, "pagination": result["pagination"]})


@bp.route("/charts/status")
def get_status_distribution():
    """
    Get status distribution data for bar chart.

    Returns:
        JSON response with labels and data arrays
    """
    chart_service = ChartService()
    data = chart_service.get_status_distribution()
    return jsonify(data)


@bp.route("/charts/priority")
def get_priority_distribution():
    """
    Get priority distribution data for pie chart.

    Returns:
        JSON response with labels and data arrays
    """
    chart_service = ChartService()
    data = chart_service.get_priority_distribution()
    return jsonify(data)
