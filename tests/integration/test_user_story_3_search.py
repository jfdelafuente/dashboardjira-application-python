"""
Integration tests for User Story 3: Browse and Search Issue Details.

End-to-end test that validates the complete user journey:
1. User loads the dashboard page
2. Dashboard displays issue table with all issues
3. User can search by text
4. User can filter by priority
5. User can combine filters
6. Pagination works correctly

Success Criteria:
    - Table section is visible with issues
    - Search functionality works
    - Priority filter works
    - Pagination controls work
    - Combined filters work
"""

import pytest
from app.models.issue import Issue
from app.models.team_member import TeamMember


class TestUserStory3Search:
    """Test complete user journey for browsing and searching issues."""

    def test_dashboard_has_table_section(self, client):
        """Test that dashboard HTML contains table section."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        assert response.status_code == 200
        assert "table-section" in html

    def test_dashboard_has_search_field(self, client):
        """Test that dashboard contains search input field."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        assert 'type="search"' in html or 'type="text"' in html
        assert "search" in html.lower()

    def test_dashboard_has_priority_filter(self, client):
        """Test that dashboard contains priority filter dropdown."""
        response = client.get("/")
        html = response.data.decode("utf-8")

        assert "<select" in html
        assert "priority" in html.lower()

    def test_issues_api_endpoint_returns_json(self, client, db, init_database):
        """Test that /api/issues endpoint returns JSON."""
        response = client.get("/api/issues")

        assert response.status_code == 200
        assert response.content_type == "application/json"

    def test_issues_api_returns_correct_structure(self, client, db, init_database):
        """Test that issues API has correct JSON structure."""
        response = client.get("/api/issues")
        data = response.get_json()

        assert "issues" in data
        assert "pagination" in data
        assert isinstance(data["issues"], list)
        assert isinstance(data["pagination"], dict)

    def test_issues_api_returns_all_issues(self, client, db, init_database):
        """Test that API returns all issues when no filters."""
        # Create 3 test issues
        for i in range(3):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Test issue {i}",
                status="To Do",
                priority="Medium",
            )
            db.session.add(issue)
        db.session.commit()

        response = client.get("/api/issues")
        data = response.get_json()

        assert len(data["issues"]) == 3

    def test_search_filter_by_text(self, client, db, init_database):
        """Test that text search filter works via API."""
        issue1 = Issue(
            jira_key="SUP-1",
            summary="Login authentication bug",
            status="To Do",
            priority="High",
        )
        issue2 = Issue(
            jira_key="SUP-2",
            summary="Dashboard performance",
            status="In Progress",
            priority="Medium",
        )
        db.session.add_all([issue1, issue2])
        db.session.commit()

        response = client.get("/api/issues?search=Login")
        data = response.get_json()

        assert len(data["issues"]) == 1
        assert "Login" in data["issues"][0]["summary"]

    def test_filter_by_priority(self, client, db, init_database):
        """Test that priority filter works via API."""
        critical = Issue(
            jira_key="SUP-1",
            summary="Critical bug",
            status="To Do",
            priority="Critical",
        )
        medium = Issue(
            jira_key="SUP-2",
            summary="Medium bug",
            status="To Do",
            priority="Medium",
        )
        db.session.add_all([critical, medium])
        db.session.commit()

        response = client.get("/api/issues?priority=Critical")
        data = response.get_json()

        assert len(data["issues"]) == 1
        assert data["issues"][0]["priority"] == "Critical"

    def test_combined_filters(self, client, db, init_database):
        """Test that search and priority filters work together."""
        issue1 = Issue(
            jira_key="SUP-1",
            summary="Login bug critical",
            status="To Do",
            priority="Critical",
        )
        issue2 = Issue(
            jira_key="SUP-2",
            summary="Login bug medium",
            status="To Do",
            priority="Medium",
        )
        issue3 = Issue(
            jira_key="SUP-3",
            summary="Dashboard critical",
            status="To Do",
            priority="Critical",
        )
        db.session.add_all([issue1, issue2, issue3])
        db.session.commit()

        response = client.get("/api/issues?search=Login&priority=Critical")
        data = response.get_json()

        assert len(data["issues"]) == 1
        assert data["issues"][0]["jira_key"] == "SUP-1"

    def test_pagination_works(self, client, db, init_database):
        """Test that pagination returns correct page."""
        # Create 15 issues
        for i in range(15):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Issue {i}",
                status="To Do",
                priority="Medium",
            )
            db.session.add(issue)
        db.session.commit()

        response = client.get("/api/issues?page=1&per_page=10")
        data = response.get_json()

        assert len(data["issues"]) == 10
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["total_items"] == 15
        assert data["pagination"]["total_pages"] == 2

    def test_pagination_second_page(self, client, db, init_database):
        """Test that second page returns remaining items."""
        # Create 15 issues
        for i in range(15):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Issue {i}",
                status="To Do",
                priority="Medium",
            )
            db.session.add(issue)
        db.session.commit()

        response = client.get("/api/issues?page=2&per_page=10")
        data = response.get_json()

        assert len(data["issues"]) == 5
        assert data["pagination"]["page"] == 2

    def test_issue_includes_assignee_info(self, client, db, init_database):
        """Test that issue JSON includes assignee information."""
        member = TeamMember(
            jira_id="john.doe", name="John Doe", email="john@example.com"
        )
        db.session.add(member)
        db.session.flush()

        issue = Issue(
            jira_key="SUP-1",
            summary="Test issue",
            status="To Do",
            priority="High",
            assignee_id=member.id,
        )
        db.session.add(issue)
        db.session.commit()

        response = client.get("/api/issues")
        data = response.get_json()

        assert len(data["issues"]) == 1
        assert "assignee_name" in data["issues"][0]
        assert data["issues"][0]["assignee_name"] == "John Doe"

    def test_unassigned_issue_shows_null_assignee(self, client, db, init_database):
        """Test that unassigned issues show null assignee."""
        issue = Issue(
            jira_key="SUP-1",
            summary="Unassigned issue",
            status="To Do",
            priority="Medium",
            assignee_id=None,
        )
        db.session.add(issue)
        db.session.commit()

        response = client.get("/api/issues")
        data = response.get_json()

        assert data["issues"][0]["assignee_name"] is None

    def test_empty_search_returns_no_results(self, client, db, init_database):
        """Test that search with no matches returns empty list."""
        issue = Issue(
            jira_key="SUP-1",
            summary="Test issue",
            status="To Do",
            priority="Medium",
        )
        db.session.add(issue)
        db.session.commit()

        response = client.get("/api/issues?search=NonexistentText")
        data = response.get_json()

        assert len(data["issues"]) == 0
        assert data["pagination"]["total_items"] == 0
