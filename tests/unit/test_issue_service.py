"""
Unit tests for Issue service filtering and pagination.

Tests:
    - filter_by_text() searches in jira_key and summary
    - filter_by_priority() filters by priority value
    - get_paginated_issues() returns correct page of results
"""

import pytest
from app.services.issue_service import IssueService
from app.models.issue import Issue


class TestIssueServiceFiltering:
    """Test Issue service filtering methods."""

    def test_filter_by_text_searches_jira_key(self, db, init_database):
        """Test that filter_by_text finds issues by jira_key."""
        # Create test issues
        issue1 = Issue(
            jira_key="SUP-123",
            summary="Login bug",
            status="To Do",
            priority="High",
        )
        issue2 = Issue(
            jira_key="HELP-456",
            summary="Dashboard error",
            status="In Progress",
            priority="Medium",
        )
        db.session.add_all([issue1, issue2])
        db.session.commit()

        service = IssueService()
        results = service.filter_by_text("SUP-123")

        assert len(results) == 1
        assert results[0].jira_key == "SUP-123"

    def test_filter_by_text_searches_summary(self, db, init_database):
        """Test that filter_by_text finds issues by summary content."""
        issue1 = Issue(
            jira_key="SUP-1",
            summary="Login bug with authentication",
            status="To Do",
            priority="High",
        )
        issue2 = Issue(
            jira_key="SUP-2",
            summary="Dashboard performance issue",
            status="In Progress",
            priority="Medium",
        )
        db.session.add_all([issue1, issue2])
        db.session.commit()

        service = IssueService()
        results = service.filter_by_text("Dashboard")

        assert len(results) == 1
        assert "Dashboard" in results[0].summary

    def test_filter_by_text_is_case_insensitive(self, db, init_database):
        """Test that text search is case-insensitive."""
        issue = Issue(
            jira_key="SUP-1",
            summary="Login Bug",
            status="To Do",
            priority="High",
        )
        db.session.add(issue)
        db.session.commit()

        service = IssueService()
        results = service.filter_by_text("login")

        assert len(results) == 1
        assert results[0].summary == "Login Bug"

    def test_filter_by_text_returns_all_when_empty(self, db, init_database):
        """Test that empty search text returns all issues."""
        issue1 = Issue(
            jira_key="SUP-1", summary="Issue 1", status="To Do", priority="High"
        )
        issue2 = Issue(
            jira_key="SUP-2", summary="Issue 2", status="Done", priority="Low"
        )
        db.session.add_all([issue1, issue2])
        db.session.commit()

        service = IssueService()
        results = service.filter_by_text("")

        assert len(results) == 2

    def test_filter_by_priority_returns_matching_issues(self, db, init_database):
        """Test that filter_by_priority returns only matching priority."""
        critical = Issue(
            jira_key="SUP-1", summary="Critical", status="To Do", priority="Critical"
        )
        high = Issue(jira_key="SUP-2", summary="High", status="To Do", priority="High")
        medium = Issue(
            jira_key="SUP-3", summary="Medium", status="Done", priority="Medium"
        )
        db.session.add_all([critical, high, medium])
        db.session.commit()

        service = IssueService()
        results = service.filter_by_priority("Critical")

        assert len(results) == 1
        assert results[0].priority == "Critical"

    def test_filter_by_priority_returns_all_when_none(self, db, init_database):
        """Test that None priority filter returns all issues."""
        issue1 = Issue(
            jira_key="SUP-1", summary="Issue 1", status="To Do", priority="High"
        )
        issue2 = Issue(
            jira_key="SUP-2", summary="Issue 2", status="Done", priority="Low"
        )
        db.session.add_all([issue1, issue2])
        db.session.commit()

        service = IssueService()
        results = service.filter_by_priority(None)

        assert len(results) == 2

    def test_get_paginated_issues_returns_correct_page(self, db, init_database):
        """Test that pagination returns correct slice of results."""
        # Create 10 issues
        for i in range(10):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Issue {i}",
                status="To Do",
                priority="Medium",
            )
            db.session.add(issue)
        db.session.commit()

        service = IssueService()
        result = service.get_paginated_issues(page=1, per_page=5)

        assert len(result["issues"]) == 5
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["per_page"] == 5
        assert result["pagination"]["total_items"] == 10
        assert result["pagination"]["total_pages"] == 2

    def test_get_paginated_issues_returns_second_page(self, db, init_database):
        """Test that pagination returns correct second page."""
        # Create 7 issues
        for i in range(7):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Issue {i}",
                status="To Do",
                priority="Medium",
            )
            db.session.add(issue)
        db.session.commit()

        service = IssueService()
        result = service.get_paginated_issues(page=2, per_page=5)

        assert len(result["issues"]) == 2  # Only 2 items on page 2
        assert result["pagination"]["page"] == 2
        assert result["pagination"]["total_pages"] == 2

    def test_combined_filters_text_and_priority(self, db, init_database):
        """Test that multiple filters can be combined."""
        issue1 = Issue(
            jira_key="SUP-1",
            summary="Login bug",
            status="To Do",
            priority="Critical",
        )
        issue2 = Issue(
            jira_key="SUP-2",
            summary="Login slow",
            status="In Progress",
            priority="Medium",
        )
        issue3 = Issue(
            jira_key="SUP-3",
            summary="Dashboard bug",
            status="To Do",
            priority="Critical",
        )
        db.session.add_all([issue1, issue2, issue3])
        db.session.commit()

        service = IssueService()
        # Filter by text "Login" AND priority "Critical"
        results = service.get_paginated_issues(
            search="Login", priority="Critical", page=1, per_page=10
        )

        assert len(results["issues"]) == 1
        assert results["issues"][0].jira_key == "SUP-1"
