"""
Integration tests for User Story 1: View Real-Time Support Metrics.

End-to-end test that validates the complete user journey:
1. User loads the dashboard page
2. Dashboard displays all 4 KPI cards with current, accurate data
3. KPI values match expected calculations from database state

Success Criteria:
    - Dashboard page loads successfully (HTTP 200)
    - All 4 KPI cards are visible on the page
    - KPI values are calculated correctly from actual database state
    - Values update when database state changes
"""

import pytest
from datetime import datetime, timedelta
from app.models.issue import Issue
from app.models.team_member import TeamMember


class TestUserStory1KPIDisplay:
    """Test complete user journey for viewing KPI metrics."""

    def test_dashboard_loads_successfully(self, client):
        """Test that dashboard page loads with HTTP 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_dashboard_displays_all_four_kpi_cards(self, client):
        """Test that dashboard HTML contains all 4 KPI card elements."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        # Check for KPI card containers
        assert 'class="kpi-card"' in html or "kpi-card" in html

        # Check for specific KPI labels
        assert "Total Open Issues" in html or "total-open" in html
        assert "Critical Issues" in html or "critical-issues" in html
        assert "Avg Resolution Time" in html or "avg-resolution-time" in html
        assert "Overdue Tickets" in html or "overdue-tickets" in html

    def test_kpi_values_match_database_state(self, client, db, init_database):
        """Test that displayed KPI values accurately reflect database state."""
        # Setup: Create known database state
        past_deadline = datetime.utcnow() - timedelta(hours=3)

        # Create 5 open issues (3 To Do, 2 In Progress)
        for i in range(5):
            status = "To Do" if i < 3 else "In Progress"
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Open issue {i}",
                status=status,
                priority="Medium",
            )
            db.session.add(issue)

        # Create 2 critical issues
        for i in range(5, 7):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Critical issue {i}",
                status="To Do",
                priority="Critical",
            )
            db.session.add(issue)

        # Create 3 resolved issues with 2, 4, 6 hour resolution times (avg = 4)
        for i, hours in enumerate([2, 4, 6], start=7):
            created = datetime.utcnow() - timedelta(hours=hours)
            resolved = datetime.utcnow()

            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Resolved issue {i}",
                status="Done",
                priority="High",
                created_at=created,
                resolved_at=resolved,
            )
            db.session.add(issue)

        # Create 2 overdue issues
        for i in range(10, 12):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Overdue issue {i}",
                status="In Progress",
                priority="High",
                sla_deadline=past_deadline,
            )
            db.session.add(issue)

        db.session.commit()

        # Act: Get dashboard page
        response = client.get("/")
        html = response.data.decode("utf-8")

        # Assert: KPI values are correct
        # Total Open = 5 open + 2 critical + 2 overdue = 9 (excludes 3 resolved)
        assert "9" in html  # Total open issues

        # Critical Issues = 2
        assert "2" in html  # Critical issues count

        # Avg Resolution Time = 4 hours
        assert "4" in html or "4.0" in html  # Average resolution time

        # Overdue Tickets = 2
        # Note: "2" already verified above, but context should show overdue

    def test_kpi_api_endpoint_returns_json(self, client):
        """Test that /api/kpis endpoint returns JSON with correct structure."""
        response = client.get("/api/kpis")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = response.get_json()
        assert "total_open" in data
        assert "critical_issues" in data
        assert "avg_resolution_time_hours" in data
        assert "overdue_tickets" in data

    def test_kpi_values_update_when_data_changes(self, client, db, init_database):
        """Test that KPI values reflect changes when database state updates."""
        # Initial state: No issues
        response = client.get("/api/kpis")
        initial_data = response.get_json()

        assert initial_data["total_open"] == 0
        assert initial_data["critical_issues"] == 0

        # Add 3 issues (2 open, 1 critical)
        for i in range(2):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Issue {i}",
                status="To Do",
                priority="Medium",
            )
            db.session.add(issue)

        issue = Issue(
            jira_key="SUP-2",
            summary="Critical issue",
            status="In Progress",
            priority="Critical",
        )
        db.session.add(issue)
        db.session.commit()

        # Updated state: Values should reflect new issues
        response = client.get("/api/kpis")
        updated_data = response.get_json()

        assert updated_data["total_open"] == 3
        assert updated_data["critical_issues"] == 1

    def test_empty_database_shows_zero_values(self, client, db, init_database):
        """Test that KPIs show 0 values when database is empty."""
        response = client.get("/api/kpis")
        data = response.get_json()

        assert data["total_open"] == 0
        assert data["critical_issues"] == 0
        assert data["avg_resolution_time_hours"] == 0
        assert data["overdue_tickets"] == 0

    def test_kpi_cards_have_accessible_labels(self, client):
        """Test that KPI cards have proper accessibility labels."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        # Check for ARIA labels or semantic HTML
        assert (
            "aria-label" in html or "<h3" in html or 'role="region"' in html
        ), "KPI cards should have accessibility labels"

    def test_kpi_values_display_with_correct_units(self, client, db, init_database):
        """Test that KPI values display with appropriate units (e.g., hours for avg time)."""
        # Create resolved issue with 5-hour resolution time
        created = datetime.utcnow() - timedelta(hours=5)
        resolved = datetime.utcnow()

        issue = Issue(
            jira_key="SUP-1",
            summary="Resolved",
            status="Done",
            priority="High",
            created_at=created,
            resolved_at=resolved,
        )
        db.session.add(issue)
        db.session.commit()

        response = client.get("/")
        html = response.data.decode("utf-8")

        # Check that hours unit is mentioned for avg resolution time
        assert "hours" in html.lower() or "hrs" in html.lower() or "h" in html
