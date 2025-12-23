"""
Unit tests for Issue model.

Tests:
    - Status enum validation (To Do, In Progress, Done)
    - Priority enum validation (Critical, High, Medium, Low)
    - Jira key pattern validation (PROJECT-NUMBER format)
    - Summary length validation (1-500 characters)
    - is_overdue property calculation
    - resolution_time_hours property calculation
"""

import pytest
from datetime import datetime, timedelta
from app.models.issue import Issue
from app.models.team_member import TeamMember


class TestIssueValidation:
    """Test Issue model validation rules."""

    def test_valid_issue_creation(self, init_database):
        """Test creating a valid issue."""
        issue = Issue(
            jira_key="SUP-1234",
            summary="Test issue",
            status="To Do",
            priority="Medium",
        )
        assert issue.jira_key == "SUP-1234"
        assert issue.summary == "Test issue"
        assert issue.status == "To Do"
        assert issue.priority == "Medium"

    def test_invalid_status_raises_error(self, init_database):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid status"):
            Issue(
                jira_key="SUP-1234",
                summary="Test issue",
                status="InvalidStatus",
                priority="Medium",
            )

    def test_valid_statuses(self, init_database):
        """Test all valid status values."""
        valid_statuses = ["To Do", "In Progress", "Done"]
        for status in valid_statuses:
            issue = Issue(
                jira_key=f"SUP-{valid_statuses.index(status)}",
                summary="Test",
                status=status,
                priority="Medium",
            )
            assert issue.status == status

    def test_invalid_priority_raises_error(self, init_database):
        """Test that invalid priority raises ValueError."""
        with pytest.raises(ValueError, match="Invalid priority"):
            Issue(
                jira_key="SUP-1234",
                summary="Test issue",
                status="To Do",
                priority="InvalidPriority",
            )

    def test_valid_priorities(self, init_database):
        """Test all valid priority values."""
        valid_priorities = ["Critical", "High", "Medium", "Low"]
        for priority in valid_priorities:
            issue = Issue(
                jira_key=f"SUP-{valid_priorities.index(priority)}",
                summary="Test",
                status="To Do",
                priority=priority,
            )
            assert issue.priority == priority

    def test_invalid_jira_key_format_raises_error(self, init_database):
        """Test that invalid jira_key format raises ValueError."""
        invalid_keys = ["sup-123", "123-SUP", "SUPPORT", "SUP_123"]
        for invalid_key in invalid_keys:
            with pytest.raises(ValueError, match="Invalid jira_key format"):
                Issue(
                    jira_key=invalid_key,
                    summary="Test",
                    status="To Do",
                    priority="Medium",
                )

    def test_valid_jira_key_formats(self, init_database):
        """Test valid jira_key formats (PROJECT-NUMBER)."""
        valid_keys = ["SUP-1", "HELP-999", "BUG-12345", "ABC-1"]
        for valid_key in valid_keys:
            issue = Issue(
                jira_key=valid_key,
                summary="Test",
                status="To Do",
                priority="Medium",
            )
            assert issue.jira_key == valid_key

    def test_summary_too_short_raises_error(self, init_database):
        """Test that empty summary raises ValueError."""
        with pytest.raises(ValueError, match="Summary length"):
            Issue(
                jira_key="SUP-1234",
                summary="",
                status="To Do",
                priority="Medium",
            )

    def test_summary_too_long_raises_error(self, init_database):
        """Test that summary >500 chars raises ValueError."""
        with pytest.raises(ValueError, match="Summary length"):
            Issue(
                jira_key="SUP-1234",
                summary="x" * 501,
                status="To Do",
                priority="Medium",
            )


class TestIssueProperties:
    """Test Issue model computed properties."""

    def test_is_overdue_when_sla_deadline_passed(self, init_database):
        """Test is_overdue returns True when SLA deadline passed and not resolved."""
        past_deadline = datetime.utcnow() - timedelta(hours=1)
        issue = Issue(
            jira_key="SUP-1234",
            summary="Overdue issue",
            status="In Progress",
            priority="Critical",
            sla_deadline=past_deadline,
        )
        assert issue.is_overdue is True

    def test_is_overdue_false_when_resolved(self, init_database):
        """Test is_overdue returns False when issue is resolved (status=Done)."""
        past_deadline = datetime.utcnow() - timedelta(hours=1)
        issue = Issue(
            jira_key="SUP-1234",
            summary="Resolved issue",
            status="Done",
            priority="Critical",
            sla_deadline=past_deadline,
            resolved_at=datetime.utcnow(),
        )
        assert issue.is_overdue is False

    def test_is_overdue_false_when_no_sla_deadline(self, init_database):
        """Test is_overdue returns False when no SLA deadline set."""
        issue = Issue(
            jira_key="SUP-1234",
            summary="No SLA",
            status="In Progress",
            priority="Low",
            sla_deadline=None,
        )
        assert issue.is_overdue is False

    def test_is_overdue_false_when_deadline_in_future(self, init_database):
        """Test is_overdue returns False when SLA deadline is in future."""
        future_deadline = datetime.utcnow() + timedelta(hours=1)
        issue = Issue(
            jira_key="SUP-1234",
            summary="On time",
            status="In Progress",
            priority="Medium",
            sla_deadline=future_deadline,
        )
        assert issue.is_overdue is False

    def test_resolution_time_hours_when_resolved(self, init_database):
        """Test resolution_time_hours calculates correctly for resolved issues."""
        created = datetime.utcnow() - timedelta(hours=5)
        resolved = datetime.utcnow()
        issue = Issue(
            jira_key="SUP-1234",
            summary="Resolved",
            status="Done",
            priority="High",
            created_at=created,
            resolved_at=resolved,
        )
        # Should be approximately 5 hours
        assert 4.9 < issue.resolution_time_hours < 5.1

    def test_resolution_time_hours_none_when_not_resolved(self, init_database):
        """Test resolution_time_hours returns None for unresolved issues."""
        issue = Issue(
            jira_key="SUP-1234",
            summary="Unresolved",
            status="In Progress",
            priority="Medium",
            resolved_at=None,
        )
        assert issue.resolution_time_hours is None
