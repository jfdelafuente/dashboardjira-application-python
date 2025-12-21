"""
TeamMember model representing support team members.

Attributes:
    id: Primary key (auto-increment)
    jira_id: Unique Jira user ID
    name: Full name (1-100 chars)
    email: Email address (optional, must be valid format)
    created_at: Timestamp when member was first added
    updated_at: Timestamp of last update (auto-updated)

Properties:
    workload: Count of assigned open issues (status != Done)
"""

from app import db
from datetime import datetime
import re


class TeamMember(db.Model):
    """Support team member model."""

    __tablename__ = "team_members"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core fields
    jira_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    assigned_issues = db.relationship(
        "Issue", back_populates="assignee", lazy="dynamic"
    )

    # Validation constants
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, **kwargs):
        """Initialize and validate TeamMember instance."""
        super().__init__(**kwargs)
        self.validate()

    def validate(self):
        """
        Validate TeamMember fields.

        Raises:
            ValueError: If validation fails
        """
        # Validate name length
        if not (1 <= len(self.name) <= 100):
            raise ValueError(
                f"Name length must be 1-100 characters, got {len(self.name)}"
            )

        # Validate email format (if provided)
        if self.email and not self.EMAIL_PATTERN.match(self.email):
            raise ValueError(f"Invalid email format: {self.email}")

    @property
    def workload(self):
        """
        Count of assigned open issues.

        Returns:
            int: Number of assigned issues with status != Done
        """
        return self.assigned_issues.filter(db.text("status != 'Done'")).count()

    def __repr__(self):
        """String representation of TeamMember."""
        return f"<TeamMember {self.name} ({self.jira_id})>"
