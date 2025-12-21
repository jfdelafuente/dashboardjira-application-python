"""
Issue management service.

Provides functions to manage issues and sync from Jira.
"""

from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import joinedload
from app import db
from app.models.issue import Issue
from app.models.team_member import TeamMember
from app.services.jira_service import JiraService
from app.utils.pagination import calculate_pagination


class IssueService:
    """Service for managing issues and syncing from Jira."""

    def __init__(self, jira_service: JiraService = None):
        """
        Initialize Issue service.

        Args:
            jira_service: JiraService instance (creates new one if None)
        """
        self.jira_service = jira_service or JiraService()

    def get_all_issues(self) -> List[Issue]:
        """
        Get all issues from database.

        Returns:
            List of Issue model instances
        """
        return Issue.query.all()

    def sync_from_jira(self) -> dict:
        """
        Synchronize issues from Jira to local database.

        Fetches issues from Jira and upserts them to the database.
        Also creates/updates TeamMember records for assignees.

        Returns:
            dict: Sync statistics with keys: created, updated, errors
        """
        jira_issues = self.jira_service.get_issues()

        stats = {"created": 0, "updated": 0, "errors": 0}

        for jira_issue in jira_issues:
            try:
                self._upsert_issue(jira_issue)
                stats["created"] += 1  # Simplified for now
            except Exception as e:
                stats["errors"] += 1
                print(f"Error syncing issue {jira_issue.get('jira_key')}: {str(e)}")

        db.session.commit()
        return stats

    def _upsert_issue(self, jira_issue_data: dict):
        """
        Create or update an issue from Jira data.

        Args:
            jira_issue_data: Dictionary containing issue data from Jira
        """
        # Get or create assignee if specified
        assignee = None
        if jira_issue_data.get("assignee_jira_id"):
            assignee = self._get_or_create_team_member(
                jira_id=jira_issue_data["assignee_jira_id"],
                name=jira_issue_data.get("assignee_name", "Unknown"),
                email=jira_issue_data.get("assignee_email"),
            )

        # Check if issue exists
        issue = Issue.query.filter_by(jira_key=jira_issue_data["jira_key"]).first()

        if issue:
            # Update existing issue
            issue.summary = jira_issue_data["summary"]
            issue.description = jira_issue_data.get("description")
            issue.status = jira_issue_data["status"]
            issue.priority = jira_issue_data["priority"]
            issue.assignee_id = assignee.id if assignee else None
            issue.resolved_at = jira_issue_data.get("resolved_at")
            issue.sla_deadline = jira_issue_data.get("sla_deadline")
            issue.updated_at = datetime.utcnow()
        else:
            # Create new issue
            issue = Issue(
                jira_key=jira_issue_data["jira_key"],
                summary=jira_issue_data["summary"],
                description=jira_issue_data.get("description"),
                status=jira_issue_data["status"],
                priority=jira_issue_data["priority"],
                assignee_id=assignee.id if assignee else None,
                created_at=jira_issue_data.get("created_at", datetime.utcnow()),
                resolved_at=jira_issue_data.get("resolved_at"),
                sla_deadline=jira_issue_data.get("sla_deadline"),
            )
            db.session.add(issue)

    def _get_or_create_team_member(
        self, jira_id: str, name: str, email: str = None
    ) -> TeamMember:
        """
        Get existing team member or create new one.

        Args:
            jira_id: Jira user ID
            name: Team member name
            email: Team member email (optional)

        Returns:
            TeamMember instance
        """
        member = TeamMember.query.filter_by(jira_id=jira_id).first()

        if not member:
            member = TeamMember(jira_id=jira_id, name=name, email=email)
            db.session.add(member)
            db.session.flush()  # Get ID without committing

        return member

    def filter_by_text(self, search_text: str) -> List[Issue]:
        """
        Filter issues by text search in jira_key or summary.

        Args:
            search_text: Text to search for (case-insensitive)

        Returns:
            List of Issue instances matching the search
        """
        if not search_text:
            return Issue.query.all()

        search_pattern = f"%{search_text}%"
        return Issue.query.filter(
            db.or_(
                Issue.jira_key.ilike(search_pattern),
                Issue.summary.ilike(search_pattern),
            )
        ).all()

    def filter_by_priority(self, priority: str = None) -> List[Issue]:
        """
        Filter issues by priority.

        Args:
            priority: Priority value (Critical, High, Medium, Low) or None

        Returns:
            List of Issue instances with matching priority
        """
        if not priority:
            return Issue.query.all()

        return Issue.query.filter(Issue.priority == priority).all()

    def get_paginated_issues(
        self,
        search: str = None,
        priority: str = None,
        page: int = 1,
        per_page: int = 50,
    ) -> Dict[str, Any]:
        """
        Get paginated and filtered issues.

        Args:
            search: Optional text search (jira_key or summary)
            priority: Optional priority filter
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            dict: Dictionary with keys:
                - issues: List of Issue instances for current page
                - pagination: Pagination metadata from calculate_pagination
        """
        # Start with base query
        query = Issue.query

        # Apply text search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                db.or_(
                    Issue.jira_key.ilike(search_pattern),
                    Issue.summary.ilike(search_pattern),
                )
            )

        # Apply priority filter
        if priority:
            query = query.filter(Issue.priority == priority)

        # Get total count for pagination
        total_items = query.count()

        # Apply eager loading for assignee relationship to avoid N+1 queries
        query = query.options(joinedload(Issue.assignee))

        # Apply pagination
        offset = (page - 1) * per_page
        issues = query.offset(offset).limit(per_page).all()

        # Calculate pagination metadata
        pagination = calculate_pagination(
            total_items=total_items, page=page, per_page=per_page
        )

        return {"issues": issues, "pagination": pagination}
