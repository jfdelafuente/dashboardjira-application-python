"""
Unit tests for KPI service.

Tests:
    - calculate_kpis() returns all 4 KPI metrics
    - total_open counts only non-Done issues
    - critical_issues counts only Critical priority issues
    - avg_resolution_time_hours calculates average for resolved issues
    - overdue_tickets counts issues with sla_deadline in past and not Done
"""

import pytest
from datetime import datetime, timedelta
from app.services.kpi_service import calculate_kpis
from app.models.issue import Issue


class TestCalculateKPIs:
    """Test KPI calculation logic."""

    def test_calculate_kpis_returns_all_metrics(self, db, init_database):
        """Test that calculate_kpis returns all 4 required KPI metrics."""
        kpis = calculate_kpis()

        assert "total_open" in kpis
        assert "critical_issues" in kpis
        assert "avg_resolution_time_hours" in kpis
        assert "overdue_tickets" in kpis

    def test_total_open_counts_only_non_done_issues(self, db, init_database):
        """Test that total_open counts issues with status != Done."""
        # Create 3 open issues
        for i in range(3):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Open issue {i}",
                status="In Progress" if i % 2 == 0 else "To Do",
                priority="Medium",
            )
            db.session.add(issue)

        # Create 2 closed issues
        for i in range(3, 5):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Closed issue {i}",
                status="Done",
                priority="Low",
                resolved_at=datetime.utcnow(),
            )
            db.session.add(issue)

        db.session.commit()

        kpis = calculate_kpis()
        assert kpis["total_open"] == 3

    def test_total_open_returns_zero_when_no_issues(self, db, init_database):
        """Test that total_open returns 0 when no issues exist."""
        kpis = calculate_kpis()
        assert kpis["total_open"] == 0

    def test_critical_issues_counts_only_critical_priority(self, db, init_database):
        """Test that critical_issues counts only issues with Critical priority."""
        # Create 2 critical issues
        for i in range(2):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Critical issue {i}",
                status="To Do",
                priority="Critical",
            )
            db.session.add(issue)

        # Create issues with other priorities
        for i, priority in enumerate(["High", "Medium", "Low"], start=2):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"{priority} issue {i}",
                status="In Progress",
                priority=priority,
            )
            db.session.add(issue)

        db.session.commit()

        kpis = calculate_kpis()
        assert kpis["critical_issues"] == 2

    def test_critical_issues_excludes_done_status(self, db, init_database):
        """Test that critical_issues excludes resolved Critical issues."""
        # Create 3 critical issues, 1 resolved
        for i in range(3):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Critical issue {i}",
                status="Done" if i == 0 else "To Do",
                priority="Critical",
                resolved_at=datetime.utcnow() if i == 0 else None,
            )
            db.session.add(issue)

        db.session.commit()

        kpis = calculate_kpis()
        # Should count only the 2 unresolved critical issues
        assert kpis["critical_issues"] == 2

    def test_avg_resolution_time_hours_calculates_average(self, db, init_database):
        """Test that avg_resolution_time_hours calculates correct average."""
        # Create 3 resolved issues with different resolution times
        resolution_times = [2, 4, 6]  # hours

        for i, hours in enumerate(resolution_times):
            created = datetime.utcnow() - timedelta(hours=hours)
            resolved = datetime.utcnow()

            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Resolved issue {i}",
                status="Done",
                priority="Medium",
                created_at=created,
                resolved_at=resolved,
            )
            db.session.add(issue)

        db.session.commit()

        kpis = calculate_kpis()
        # Average of [2, 4, 6] = 4.0
        assert 3.9 < kpis["avg_resolution_time_hours"] < 4.1

    def test_avg_resolution_time_hours_returns_zero_when_no_resolved_issues(
        self, db, init_database
    ):
        """Test that avg_resolution_time_hours returns 0 when no resolved issues."""
        # Create only unresolved issues
        issue = Issue(
            jira_key="SUP-1",
            summary="Unresolved",
            status="In Progress",
            priority="High",
        )
        db.session.add(issue)
        db.session.commit()

        kpis = calculate_kpis()
        assert kpis["avg_resolution_time_hours"] == 0

    def test_avg_resolution_time_hours_ignores_unresolved_issues(
        self, db, init_database
    ):
        """Test that avg_resolution_time_hours only considers resolved issues."""
        # Create 2 resolved issues
        for i in range(2):
            created = datetime.utcnow() - timedelta(hours=5)
            resolved = datetime.utcnow()

            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Resolved {i}",
                status="Done",
                priority="Medium",
                created_at=created,
                resolved_at=resolved,
            )
            db.session.add(issue)

        # Create 3 unresolved issues (should not affect average)
        for i in range(2, 5):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Unresolved {i}",
                status="To Do",
                priority="Low",
            )
            db.session.add(issue)

        db.session.commit()

        kpis = calculate_kpis()
        # Should be approximately 5 hours (ignoring unresolved issues)
        assert 4.9 < kpis["avg_resolution_time_hours"] < 5.1

    def test_overdue_tickets_counts_past_deadline_not_done(self, db, init_database):
        """Test that overdue_tickets counts issues with past SLA deadline and status != Done."""
        past_deadline = datetime.utcnow() - timedelta(hours=2)
        future_deadline = datetime.utcnow() + timedelta(hours=2)

        # Create 2 overdue issues (past deadline, not done)
        for i in range(2):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Overdue {i}",
                status="In Progress",
                priority="High",
                sla_deadline=past_deadline,
            )
            db.session.add(issue)

        # Create issue with past deadline but resolved (should not count)
        issue = Issue(
            jira_key="SUP-2",
            summary="Resolved late",
            status="Done",
            priority="Medium",
            sla_deadline=past_deadline,
            resolved_at=datetime.utcnow(),
        )
        db.session.add(issue)

        # Create issue with future deadline (should not count)
        issue = Issue(
            jira_key="SUP-3",
            summary="On time",
            status="To Do",
            priority="Low",
            sla_deadline=future_deadline,
        )
        db.session.add(issue)

        # Create issue with no SLA deadline (should not count)
        issue = Issue(
            jira_key="SUP-4",
            summary="No SLA",
            status="In Progress",
            priority="Medium",
            sla_deadline=None,
        )
        db.session.add(issue)

        db.session.commit()

        kpis = calculate_kpis()
        assert kpis["overdue_tickets"] == 2

    def test_overdue_tickets_returns_zero_when_all_on_time(self, db, init_database):
        """Test that overdue_tickets returns 0 when all issues are on time."""
        future_deadline = datetime.utcnow() + timedelta(hours=5)

        issue = Issue(
            jira_key="SUP-1",
            summary="On time",
            status="To Do",
            priority="Medium",
            sla_deadline=future_deadline,
        )
        db.session.add(issue)
        db.session.commit()

        kpis = calculate_kpis()
        assert kpis["overdue_tickets"] == 0
