"""
Issue model representing support tickets from Jira.

Attributes:
    id: Primary key (auto-increment)
    jira_key: Unique Jira issue key (e.g., "SUP-1234")
    summary: Brief description of the issue (1-500 chars)
    description: Full issue description (optional)
    status: Current workflow status (To Do, In Progress, Done)
    priority: Issue priority (Critical, High, Medium, Low)
    assignee_id: Foreign key to TeamMember (nullable)
    created_at: Timestamp when issue was created
    updated_at: Timestamp of last update (auto-updated)
    resolved_at: Timestamp when issue was resolved (nullable)
    sla_deadline: SLA deadline for resolution (nullable)
    metadata: Additional Jira fields as JSON (labels, components, etc.)

Properties:
    is_overdue: True if SLA deadline passed and not resolved
    resolution_time_hours: Hours from creation to resolution (None if unresolved)
"""

from app import db
from datetime import datetime
import re


class Issue(db.Model):
    """Support ticket/issue model."""

    __tablename__ = "issues"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core fields
    jira_key = db.Column(db.String(20), unique=True, nullable=False, index=True)
    summary = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)

    # Workflow fields
    status = db.Column(db.String(20), nullable=False, default="To Do", index=True)
    priority = db.Column(db.String(20), nullable=False, default="Medium", index=True)

    # Assignment
    assignee_id = db.Column(
        db.Integer,
        db.ForeignKey("team_members.id", ondelete="SET NULL"),
        index=True,
    )

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    resolved_at = db.Column(db.DateTime)
    sla_deadline = db.Column(db.DateTime, index=True)

    # Additional data
    jira_metadata = db.Column(db.JSON, default=dict)

    # Relationships
    assignee = db.relationship("TeamMember", back_populates="assigned_issues")

    # Validation constants
    VALID_STATUSES = ["To Do", "In Progress", "Done"]
    VALID_PRIORITIES = ["Critical", "High", "Medium", "Low"]
    JIRA_KEY_PATTERN = re.compile(r"^[A-Z]+-\d+$")

    def __init__(self, **kwargs):
        """Initialize and validate Issue instance."""
        super().__init__(**kwargs)
        self.validate()

    def validate(self):
        """
        Validate Issue fields.

        Raises:
            ValueError: If validation fails
        """
        # Validate status
        if self.status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status: {self.status}. Must be one of {self.VALID_STATUSES}"
            )

        # Validate priority
        if self.priority not in self.VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority: {self.priority}. Must be one of {self.VALID_PRIORITIES}"
            )

        # Validate jira_key format
        if not self.JIRA_KEY_PATTERN.match(self.jira_key):
            raise ValueError(
                f"Invalid jira_key format: {self.jira_key}. Must match pattern PROJECT-NUMBER"
            )

        # Validate summary length
        if not (1 <= len(self.summary) <= 500):
            raise ValueError(
                f"Summary length must be 1-500 characters, got {len(self.summary)}"
            )

    @property
    def is_overdue(self):
        """
        Check if issue is overdue based on SLA deadline.

        Returns:
            bool: True if SLA deadline passed and status != Done, False otherwise
        """
        if not self.sla_deadline or self.status == "Done":
            return False
        return datetime.utcnow() > self.sla_deadline

    @property
    def resolution_time_hours(self):
        """
        Calculate resolution time in hours.

        Returns:
            float: Hours from creation to resolution, or None if not resolved
        """
        if not self.resolved_at:
            return None
        delta = self.resolved_at - self.created_at
        return delta.total_seconds() / 3600

    def __repr__(self):
        """String representation of Issue."""
        summary_preview = (
            self.summary[:30] + "..." if len(self.summary) > 30 else self.summary
        )
        return f"<Issue {self.jira_key}: {summary_preview}>"
