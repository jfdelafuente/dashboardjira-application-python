"""
Integration tests for User Story 2: Visualize Issue Distribution with Charts.

End-to-end test that validates the complete user journey:
1. User loads the dashboard page
2. Dashboard displays two charts (status bar chart, priority pie chart)
3. Charts display accurate data from database
4. API endpoints return correct JSON structure

Success Criteria:
    - Dashboard page loads successfully (HTTP 200)
    - Charts section is visible with two canvas elements
    - API endpoints return correct JSON structure
    - Chart data matches database state
"""

import pytest
from app.models.issue import Issue


class TestUserStory2Charts:
    """Test complete user journey for viewing charts."""

    def test_dashboard_charts_section_exists(self, client):
        """Test that dashboard HTML contains charts section."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        assert response.status_code == 200
        assert "charts-section" in html

    def test_dashboard_has_status_chart_canvas(self, client):
        """Test that dashboard contains canvas for status chart."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        assert "status-chart" in html or "statusChart" in html

    def test_dashboard_has_priority_chart_canvas(self, client):
        """Test that dashboard contains canvas for priority chart."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        assert "priority-chart" in html or "priorityChart" in html

    def test_status_chart_api_endpoint_returns_json(self, client):
        """Test that /api/charts/status returns JSON with correct structure."""
        response = client.get("/api/charts/status")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = response.get_json()
        assert "labels" in data
        assert "data" in data
        assert isinstance(data["labels"], list)
        assert isinstance(data["data"], list)

    def test_status_chart_api_returns_all_statuses(self, client):
        """Test that status chart API returns all 3 status labels."""
        response = client.get("/api/charts/status")
        data = response.get_json()

        assert data["labels"] == ["To Do", "In Progress", "Done"]
        assert len(data["data"]) == 3

    def test_priority_chart_api_endpoint_returns_json(self, client):
        """Test that /api/charts/priority returns JSON with correct structure."""
        response = client.get("/api/charts/priority")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = response.get_json()
        assert "labels" in data
        assert "data" in data
        assert isinstance(data["labels"], list)
        assert isinstance(data["data"], list)

    def test_priority_chart_api_returns_all_priorities(self, client):
        """Test that priority chart API returns all 4 priority labels."""
        response = client.get("/api/charts/priority")
        data = response.get_json()

        assert data["labels"] == ["Critical", "High", "Medium", "Low"]
        assert len(data["data"]) == 4

    def test_chart_data_matches_database_state(self, client, db, init_database):
        """Test that chart API data accurately reflects database state."""
        # Create known database state
        # Status: 2 To Do, 1 In Progress, 1 Done
        # Priority: 1 Critical, 1 High, 1 Medium, 1 Low

        issue1 = Issue(
            jira_key="SUP-1",
            summary="Test 1",
            status="To Do",
            priority="Critical",
        )
        issue2 = Issue(
            jira_key="SUP-2",
            summary="Test 2",
            status="To Do",
            priority="High",
        )
        issue3 = Issue(
            jira_key="SUP-3",
            summary="Test 3",
            status="In Progress",
            priority="Medium",
        )
        issue4 = Issue(
            jira_key="SUP-4",
            summary="Test 4",
            status="Done",
            priority="Low",
        )

        db.session.add_all([issue1, issue2, issue3, issue4])
        db.session.commit()

        # Check status distribution
        status_response = client.get("/api/charts/status")
        status_data = status_response.get_json()

        assert status_data["data"] == [2, 1, 1]  # To Do, In Progress, Done

        # Check priority distribution (only open issues)
        priority_response = client.get("/api/charts/priority")
        priority_data = priority_response.get_json()

        # Only 3 open issues: Critical, High, Medium (Low is Done)
        assert priority_data["data"] == [1, 1, 1, 0]  # Critical, High, Medium, Low

    def test_empty_database_returns_zeros(self, client, db, init_database):
        """Test that charts return zeros when database is empty."""
        status_response = client.get("/api/charts/status")
        status_data = status_response.get_json()

        assert status_data["data"] == [0, 0, 0]

        priority_response = client.get("/api/charts/priority")
        priority_data = priority_response.get_json()

        assert priority_data["data"] == [0, 0, 0, 0]

    def test_dashboard_loads_chartjs_library(self, client):
        """Test that Chart.js library is loaded in dashboard."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        # Check for Chart.js CDN
        assert "chart.js" in html.lower() or "chartjs" in html.lower()
