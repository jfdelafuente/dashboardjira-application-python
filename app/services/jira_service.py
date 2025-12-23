"""
Jira integration service.

Provides functions to fetch issues from Jira API with mock data support for testing.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any


class JiraService:
    """Service for fetching issues from Jira API or mock data."""

    def __init__(self, use_mock: bool = None):
        """
        Initialize Jira service.

        Args:
            use_mock: If True, use mock data. If None, check environment variable.
        """
        if use_mock is None:
            use_mock = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
        self.use_mock = use_mock

    def get_issues(self) -> List[Dict[str, Any]]:
        """
        Fetch issues from Jira or return mock data.

        Returns:
            List of issue dictionaries with keys: jira_key, summary, status, priority,
            assignee_jira_id, assignee_name, created_at, resolved_at, sla_deadline
        """
        if self.use_mock:
            return self._get_mock_issues()
        else:
            return self._fetch_from_jira()

    def _get_mock_issues(self) -> List[Dict[str, Any]]:
        """
        Generate mock issue data for testing and development.

        Returns:
            List of mock issue dictionaries
        """
        now = datetime.utcnow()
        past_deadline = now - timedelta(hours=2)
        future_deadline = now + timedelta(hours=4)

        mock_issues = [
            # Open issues
            {
                "jira_key": "SUP-001",
                "summary": "Application crashes on startup",
                "description": "Users report application crashes when launching on Windows 10",
                "status": "To Do",
                "priority": "Critical",
                "assignee_jira_id": "john.doe",
                "assignee_name": "John Doe",
                "assignee_email": "john.doe@example.com",
                "created_at": now - timedelta(hours=3),
                "resolved_at": None,
                "sla_deadline": past_deadline,  # Overdue
            },
            {
                "jira_key": "SUP-002",
                "summary": "Unable to login with SSO",
                "description": "SSO authentication failing for enterprise users",
                "status": "In Progress",
                "priority": "High",
                "assignee_jira_id": "jane.smith",
                "assignee_name": "Jane Smith",
                "assignee_email": "jane.smith@example.com",
                "created_at": now - timedelta(hours=5),
                "resolved_at": None,
                "sla_deadline": future_deadline,
            },
            {
                "jira_key": "SUP-003",
                "summary": "Dashboard loading slowly",
                "description": "Dashboard takes 10+ seconds to load with large datasets",
                "status": "To Do",
                "priority": "Medium",
                "assignee_jira_id": "bob.wilson",
                "assignee_name": "Bob Wilson",
                "assignee_email": "bob.wilson@example.com",
                "created_at": now - timedelta(hours=8),
                "resolved_at": None,
                "sla_deadline": None,
            },
            {
                "jira_key": "SUP-004",
                "summary": "Email notifications not sending",
                "description": "Users not receiving notification emails",
                "status": "In Progress",
                "priority": "Critical",
                "assignee_jira_id": "alice.brown",
                "assignee_name": "Alice Brown",
                "assignee_email": "alice.brown@example.com",
                "created_at": now - timedelta(hours=1),
                "resolved_at": None,
                "sla_deadline": past_deadline,  # Overdue
            },
            {
                "jira_key": "SUP-005",
                "summary": "Feature request: Dark mode",
                "description": "Users requesting dark mode theme option",
                "status": "To Do",
                "priority": "Low",
                "assignee_jira_id": None,
                "assignee_name": None,
                "assignee_email": None,
                "created_at": now - timedelta(days=2),
                "resolved_at": None,
                "sla_deadline": None,
            },
            # Resolved issues
            {
                "jira_key": "SUP-006",
                "summary": "Fix typo in welcome message",
                "description": "Spelling error in user onboarding flow",
                "status": "Done",
                "priority": "Low",
                "assignee_jira_id": "john.doe",
                "assignee_name": "John Doe",
                "assignee_email": "john.doe@example.com",
                "created_at": now - timedelta(hours=10),
                "resolved_at": now - timedelta(hours=8),  # 2 hours resolution time
                "sla_deadline": None,
            },
            {
                "jira_key": "SUP-007",
                "summary": "Update API documentation",
                "description": "Add examples to REST API documentation",
                "status": "Done",
                "priority": "Medium",
                "assignee_jira_id": "jane.smith",
                "assignee_name": "Jane Smith",
                "assignee_email": "jane.smith@example.com",
                "created_at": now - timedelta(hours=12),
                "resolved_at": now - timedelta(hours=6),  # 6 hours resolution time
                "sla_deadline": None,
            },
            {
                "jira_key": "SUP-008",
                "summary": "Database connection timeout",
                "description": "Connection pool exhaustion under high load",
                "status": "Done",
                "priority": "High",
                "assignee_jira_id": "bob.wilson",
                "assignee_name": "Bob Wilson",
                "assignee_email": "bob.wilson@example.com",
                "created_at": now - timedelta(hours=20),
                "resolved_at": now - timedelta(hours=16),  # 4 hours resolution time
                "sla_deadline": future_deadline,
            },
        ]

        return mock_issues

    def _fetch_from_jira(self) -> List[Dict[str, Any]]:
        """
        Fetch issues from Jira API.

        Returns:
            List of issue dictionaries from Jira
        """
        from jira import JIRA
        import urllib3

        jira_server = os.getenv("JIRA_SERVER")
        jira_email = os.getenv("JIRA_EMAIL")
        jira_token = os.getenv("JIRA_API_TOKEN")
        jira_username = os.getenv("JIRA_USERNAME")
        jira_password = os.getenv("JIRA_PASSWORD")
        project_key = os.getenv("JIRA_PROJECT_KEY")

        if not jira_server or not project_key:
            raise ValueError(
                "Missing required Jira configuration. "
                "Set JIRA_SERVER and JIRA_PROJECT_KEY in .env"
            )

        # Determine authentication method
        has_user_pass = bool(jira_username and jira_password)
        has_email_token = bool(jira_email and jira_token)

        if not has_user_pass and not has_email_token:
            raise ValueError(
                "Missing Jira authentication credentials. "
                "Set either JIRA_USERNAME + JIRA_PASSWORD or JIRA_EMAIL + JIRA_API_TOKEN in .env"
            )

        # Configure SSL verification
        verify_ssl = os.getenv("JIRA_VERIFY_SSL", "true").lower() in (
            "true",
            "1",
            "yes",
        )

        if not verify_ssl:
            # Suppress SSL warnings when verification is disabled
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Connect to Jira
        jira_options = {
            "server": jira_server,
            "verify": verify_ssl,
        }

        # Choose authentication method (prefer username/password for Jira Server)
        if has_user_pass:
            auth = (jira_username, jira_password)
        else:
            auth = (jira_email, jira_token)

        jira = JIRA(
            options=jira_options,
            basic_auth=auth,
            timeout=30,
        )

        # Fetch issues from project
        jql = f'project = "{project_key}" ORDER BY created DESC'
        issues = jira.search_issues(jql, maxResults=100)

        # Transform to expected format
        result = []
        for issue in issues:
            result.append(
                {
                    "jira_key": issue.key,
                    "summary": issue.fields.summary,
                    "description": getattr(issue.fields, "description", ""),
                    "status": issue.fields.status.name,
                    "priority": issue.fields.priority.name
                    if hasattr(issue.fields, "priority") and issue.fields.priority
                    else "Medium",
                    "assignee_jira_id": issue.fields.assignee.accountId
                    if hasattr(issue.fields, "assignee") and issue.fields.assignee
                    else None,
                    "assignee_name": issue.fields.assignee.displayName
                    if hasattr(issue.fields, "assignee") and issue.fields.assignee
                    else None,
                    "assignee_email": issue.fields.assignee.emailAddress
                    if hasattr(issue.fields, "assignee") and issue.fields.assignee
                    else None,
                    "created_at": datetime.fromisoformat(
                        issue.fields.created.replace("Z", "+00:00")
                    ),
                    "resolved_at": datetime.fromisoformat(
                        issue.fields.resolutiondate.replace("Z", "+00:00")
                    )
                    if hasattr(issue.fields, "resolutiondate")
                    and issue.fields.resolutiondate
                    else None,
                    "sla_deadline": None,  # SLA calculation to be implemented
                }
            )

        return result
