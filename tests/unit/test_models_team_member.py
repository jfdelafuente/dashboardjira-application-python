"""
Unit tests for TeamMember model.

Tests:
    - Jira ID uniqueness validation
    - Name length validation (1-100 characters)
    - Email format validation
    - workload property calculation
"""

import pytest
from app.models.team_member import TeamMember
from app.models.issue import Issue


class TestTeamMemberValidation:
    """Test TeamMember model validation rules."""

    def test_valid_team_member_creation(self, init_database):
        """Test creating a valid team member."""
        member = TeamMember(
            jira_id="john.doe",
            name="John Doe",
            email="john.doe@example.com",
        )
        assert member.jira_id == "john.doe"
        assert member.name == "John Doe"
        assert member.email == "john.doe@example.com"

    def test_name_too_short_raises_error(self, init_database):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Name length"):
            TeamMember(
                jira_id="test.user",
                name="",
                email="test@example.com",
            )

    def test_name_too_long_raises_error(self, init_database):
        """Test that name >100 chars raises ValueError."""
        with pytest.raises(ValueError, match="Name length"):
            TeamMember(
                jira_id="test.user",
                name="x" * 101,
                email="test@example.com",
            )

    def test_valid_name_lengths(self, init_database):
        """Test valid name lengths (1-100 characters)."""
        valid_names = ["A", "John Doe", "x" * 100]
        for idx, name in enumerate(valid_names):
            member = TeamMember(
                jira_id=f"user{idx}",
                name=name,
                email=f"user{idx}@example.com",
            )
            assert member.name == name

    def test_invalid_email_format_raises_error(self, init_database):
        """Test that invalid email format raises ValueError."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@example",
        ]
        for idx, invalid_email in enumerate(invalid_emails):
            with pytest.raises(ValueError, match="Invalid email format"):
                TeamMember(
                    jira_id=f"user{idx}",
                    name="Test User",
                    email=invalid_email,
                )

    def test_valid_email_formats(self, init_database):
        """Test valid email formats."""
        valid_emails = [
            "user@example.com",
            "first.last@company.com",
            "user+tag@domain.co.uk",
            "123@test.com",
        ]
        for idx, valid_email in enumerate(valid_emails):
            member = TeamMember(
                jira_id=f"user{idx}",
                name="Test User",
                email=valid_email,
            )
            assert member.email == valid_email

    def test_email_can_be_none(self, init_database):
        """Test that email can be None (optional field)."""
        member = TeamMember(
            jira_id="test.user",
            name="Test User",
            email=None,
        )
        assert member.email is None


class TestTeamMemberWorkload:
    """Test TeamMember workload property."""

    def test_workload_returns_zero_when_no_issues(self, db, init_database):
        """Test workload is 0 when team member has no assigned issues."""
        member = TeamMember(
            jira_id="test.user",
            name="Test User",
        )
        db.session.add(member)
        db.session.commit()

        assert member.workload == 0

    def test_workload_counts_only_open_issues(self, db, init_database):
        """Test workload counts only open issues (status != Done)."""
        member = TeamMember(
            jira_id="test.user",
            name="Test User",
        )
        db.session.add(member)
        db.session.commit()

        # Create 3 open issues and 2 closed issues
        for i in range(3):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Open issue {i}",
                status="In Progress",
                priority="Medium",
                assignee_id=member.id,
            )
            db.session.add(issue)

        for i in range(3, 5):
            issue = Issue(
                jira_key=f"SUP-{i}",
                summary=f"Closed issue {i}",
                status="Done",
                priority="Low",
                assignee_id=member.id,
            )
            db.session.add(issue)

        db.session.commit()

        # Workload should be 3 (only open issues)
        assert member.workload == 3
