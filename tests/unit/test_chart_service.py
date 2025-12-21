"""
Unit tests for Chart service.

Tests:
    - get_status_distribution() returns correct labels and data
    - get_priority_distribution() returns correct labels and data
    - Distribution counts match database state
"""

import pytest
from app.services.chart_service import ChartService
from app.models.issue import Issue


class TestChartService:
    """Test Chart service data generation."""

    def test_get_status_distribution_returns_correct_structure(self, db, init_database):
        """Test that get_status_distribution returns labels and data arrays."""
        chart_service = ChartService()
        result = chart_service.get_status_distribution()

        assert "labels" in result
        assert "data" in result
        assert isinstance(result["labels"], list)
        assert isinstance(result["data"], list)
        assert len(result["labels"]) == len(result["data"])

    def test_get_status_distribution_has_all_statuses(self, db, init_database):
        """Test that status distribution includes all 3 statuses."""
        chart_service = ChartService()
        result = chart_service.get_status_distribution()

        assert result["labels"] == ["To Do", "In Progress", "Done"]
        assert len(result["data"]) == 3

    def test_get_status_distribution_counts_issues_correctly(self, db, init_database):
        """Test that status distribution counts match database state."""
        # Create test data: 2 To Do, 3 In Progress, 1 Done
        statuses = [
            "To Do",
            "To Do",
            "In Progress",
            "In Progress",
            "In Progress",
            "Done",
        ]

        for i, status in enumerate(statuses):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Test issue {i}",
                status=status,
                priority="Medium",
            )
            db.session.add(issue)

        db.session.commit()

        chart_service = ChartService()
        result = chart_service.get_status_distribution()

        # Expected: [2, 3, 1] for ["To Do", "In Progress", "Done"]
        assert result["data"] == [2, 3, 1]

    def test_get_status_distribution_returns_zeros_when_no_issues(
        self, db, init_database
    ):
        """Test that status distribution returns zeros when database is empty."""
        chart_service = ChartService()
        result = chart_service.get_status_distribution()

        assert result["data"] == [0, 0, 0]

    def test_get_priority_distribution_returns_correct_structure(
        self, db, init_database
    ):
        """Test that get_priority_distribution returns labels and data arrays."""
        chart_service = ChartService()
        result = chart_service.get_priority_distribution()

        assert "labels" in result
        assert "data" in result
        assert isinstance(result["labels"], list)
        assert isinstance(result["data"], list)
        assert len(result["labels"]) == len(result["data"])

    def test_get_priority_distribution_has_all_priorities(self, db, init_database):
        """Test that priority distribution includes all 4 priorities."""
        chart_service = ChartService()
        result = chart_service.get_priority_distribution()

        assert result["labels"] == ["Critical", "High", "Medium", "Low"]
        assert len(result["data"]) == 4

    def test_get_priority_distribution_counts_issues_correctly(self, db, init_database):
        """Test that priority distribution counts match database state."""
        # Create test data: 1 Critical, 2 High, 3 Medium, 1 Low
        priorities = ["Critical", "High", "High", "Medium", "Medium", "Medium", "Low"]

        for i, priority in enumerate(priorities):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Test issue {i}",
                status="To Do",
                priority=priority,
            )
            db.session.add(issue)

        db.session.commit()

        chart_service = ChartService()
        result = chart_service.get_priority_distribution()

        # Expected: [1, 2, 3, 1] for ["Critical", "High", "Medium", "Low"]
        assert result["data"] == [1, 2, 3, 1]

    def test_get_priority_distribution_returns_zeros_when_no_issues(
        self, db, init_database
    ):
        """Test that priority distribution returns zeros when database is empty."""
        chart_service = ChartService()
        result = chart_service.get_priority_distribution()

        assert result["data"] == [0, 0, 0, 0]

    def test_get_priority_distribution_counts_only_open_issues(self, db, init_database):
        """Test that priority distribution counts only open issues (status != Done)."""
        # Create 2 Critical open, 1 Critical Done (should not count)
        issue1 = Issue(
            jira_key="SUP-1",
            summary="Critical open 1",
            status="To Do",
            priority="Critical",
        )
        issue2 = Issue(
            jira_key="SUP-2",
            summary="Critical open 2",
            status="In Progress",
            priority="Critical",
        )
        issue3 = Issue(
            jira_key="SUP-3",
            summary="Critical done",
            status="Done",
            priority="Critical",
        )
        db.session.add_all([issue1, issue2, issue3])
        db.session.commit()

        chart_service = ChartService()
        result = chart_service.get_priority_distribution()

        # Expected: [2, 0, 0, 0] - only 2 open Critical issues
        assert result["data"][0] == 2  # Critical count

    def test_get_status_distribution_includes_all_issues(self, db, init_database):
        """Test that status distribution counts all issues including Done."""
        # Create 1 of each status
        statuses = ["To Do", "In Progress", "Done"]

        for i, status in enumerate(statuses):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Test {status}",
                status=status,
                priority="Medium",
            )
            db.session.add(issue)

        db.session.commit()

        chart_service = ChartService()
        result = chart_service.get_status_distribution()

        # All statuses should have count of 1
        assert result["data"] == [1, 1, 1]
