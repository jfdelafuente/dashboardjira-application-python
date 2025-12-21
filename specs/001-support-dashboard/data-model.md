# Data Model: Support Team Dashboard

**Feature**: 001-support-dashboard
**Date**: 2025-12-21
**Purpose**: Define database entities, relationships, and validation rules

## Entity Relationship Diagram

```
┌─────────────────┐         ┌──────────────────┐
│  TeamMember     │         │     Issue        │
├─────────────────┤         ├──────────────────┤
│ id (PK)         │◄───────┤│ id (PK)          │
│ jira_id         │    1:N  │ jira_key         │
│ name            │         │ summary          │
│ email           │         │ status           │
│ created_at      │         │ priority         │
│ updated_at      │         │ assignee_id (FK) │
└─────────────────┘         │ created_at       │
                            │ updated_at       │
                            │ resolved_at      │
                            │ sla_deadline     │
                            │ metadata (JSON)  │
                            └──────────────────┘
```

## Entity: Issue

Represents a support ticket from the issue tracking system (Jira).

### Fields

| Field Name   | Type          | Nullable | Default  | Description |
|--------------|---------------|----------|----------|-------------|
| id           | Integer       | No       | Auto-inc | Primary key (internal DB ID) |
| jira_key     | String(20)    | No       | -        | Jira issue key (e.g., "SUP-1234"), unique |
| summary      | String(500)   | No       | -        | Brief description of the issue |
| description  | Text          | Yes      | NULL     | Full issue description (optional, not displayed in table) |
| status       | String(20)    | No       | 'To Do'  | Current workflow status (enum: To Do, In Progress, Done) |
| priority     | String(20)    | No       | 'Medium' | Issue priority (enum: Critical, High, Medium, Low) |
| assignee_id  | Integer (FK)  | Yes      | NULL     | Foreign key to TeamMember.id (NULL = unassigned) |
| created_at   | DateTime      | No       | UTC now  | Timestamp when issue was created in Jira |
| updated_at   | DateTime      | No       | UTC now  | Timestamp of last update (auto-updated on save) |
| resolved_at  | DateTime      | Yes      | NULL     | Timestamp when issue was resolved (status = Done) |
| sla_deadline | DateTime      | Yes      | NULL     | SLA deadline for issue resolution |
| metadata     | JSON          | Yes      | {}       | Additional Jira fields (labels, components, custom fields) |

### Indexes

- `jira_key` - Unique index for fast lookup by Jira key
- `status` - Index for filtering by status (used in KPI calculations and charts)
- `priority` - Index for filtering by priority (used in KPI calculations and charts)
- `assignee_id` - Index for filtering by team member (used in table filtering)
- `sla_deadline` - Index for finding overdue issues (WHERE sla_deadline < NOW())

### Validation Rules

1. **Status Enum**: MUST be one of: `'To Do'`, `'In Progress'`, `'Done'`
2. **Priority Enum**: MUST be one of: `'Critical'`, `'High'`, `'Medium'`, `'Low'`
3. **Jira Key Format**: MUST match pattern `^[A-Z]+-\d+$` (e.g., "SUP-123", "HELP-5678")
4. **Summary Length**: MUST be between 1 and 500 characters
5. **Resolution Timestamp**: `resolved_at` MUST be set when `status` = `'Done'`
6. **SLA Validation**: `sla_deadline` MUST be in the future when created (if set)

### Business Logic

**Overdue Calculation**:
```python
def is_overdue(issue):
    """Issue is overdue if SLA deadline passed and not resolved."""
    if not issue.sla_deadline:
        return False
    if issue.status == 'Done':
        return False
    return datetime.utcnow() > issue.sla_deadline
```

**Resolution Time Calculation**:
```python
def resolution_time_hours(issue):
    """Calculate hours from creation to resolution."""
    if not issue.resolved_at:
        return None
    delta = issue.resolved_at - issue.created_at
    return delta.total_seconds() / 3600
```

## Entity: TeamMember

Represents a person who can be assigned to work on issues.

### Fields

| Field Name | Type         | Nullable | Default | Description |
|------------|--------------|----------|---------|-------------|
| id         | Integer      | No       | Auto-inc| Primary key (internal DB ID) |
| jira_id    | String(50)   | No       | -       | Jira user ID (unique identifier from Jira) |
| name       | String(100)  | No       | -       | Full name (e.g., "Jane Doe") |
| email      | String(100)  | Yes      | NULL    | Email address (optional) |
| created_at | DateTime     | No       | UTC now | Timestamp when member was first added |
| updated_at | DateTime     | No       | UTC now | Timestamp of last update |

### Indexes

- `jira_id` - Unique index for fast lookup by Jira user ID

### Validation Rules

1. **Jira ID Uniqueness**: MUST be unique across all team members
2. **Name Length**: MUST be between 1 and 100 characters
3. **Email Format**: MUST be valid email format if provided (regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

### Relationships

- **One-to-Many with Issue**: A team member can be assigned to multiple issues, but each issue has at most one assignee
- **Cascade Behavior**: When a TeamMember is deleted, set `assignee_id` to NULL for all their issues (do NOT delete issues)

## Database Schema (SQLAlchemy Models)

### app/models/issue.py

```python
from app import db
from datetime import datetime
import re

class Issue(db.Model):
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)
    jira_key = db.Column(db.String(20), unique=True, nullable=False, index=True)
    summary = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='To Do', index=True)
    priority = db.Column(db.String(20), nullable=False, default='Medium', index=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey('team_members.id', ondelete='SET NULL'), index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    sla_deadline = db.Column(db.DateTime, index=True)
    metadata = db.Column(db.JSON, default=dict)

    # Relationship
    assignee = db.relationship('TeamMember', back_populates='assigned_issues')

    # Validation
    VALID_STATUSES = ['To Do', 'In Progress', 'Done']
    VALID_PRIORITIES = ['Critical', 'High', 'Medium', 'Low']
    JIRA_KEY_PATTERN = re.compile(r'^[A-Z]+-\d+$')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate()

    def validate(self):
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {self.VALID_STATUSES}")
        if self.priority not in self.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {self.priority}. Must be one of {self.VALID_PRIORITIES}")
        if not self.JIRA_KEY_PATTERN.match(self.jira_key):
            raise ValueError(f"Invalid jira_key format: {self.jira_key}. Must match pattern PROJECT-NUMBER")
        if not (1 <= len(self.summary) <= 500):
            raise ValueError(f"Summary length must be 1-500 characters, got {len(self.summary)}")

    @property
    def is_overdue(self):
        """Check if issue is overdue based on SLA deadline."""
        if not self.sla_deadline or self.status == 'Done':
            return False
        return datetime.utcnow() > self.sla_deadline

    @property
    def resolution_time_hours(self):
        """Calculate resolution time in hours (None if not resolved)."""
        if not self.resolved_at:
            return None
        delta = self.resolved_at - self.created_at
        return delta.total_seconds() / 3600

    def __repr__(self):
        return f'<Issue {self.jira_key}: {self.summary[:30]}...>'
```

### app/models/team_member.py

```python
from app import db
from datetime import datetime
import re

class TeamMember(db.Model):
    __tablename__ = 'team_members'

    id = db.Column(db.Integer, primary_key=True)
    jira_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    assigned_issues = db.relationship('Issue', back_populates='assignee', lazy='dynamic')

    # Validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate()

    def validate(self):
        if not (1 <= len(self.name) <= 100):
            raise ValueError(f"Name length must be 1-100 characters, got {len(self.name)}")
        if self.email and not self.EMAIL_PATTERN.match(self.email):
            raise ValueError(f"Invalid email format: {self.email}")

    @property
    def workload(self):
        """Count of assigned open issues (status != Done)."""
        return self.assigned_issues.filter(Issue.status != 'Done').count()

    def __repr__(self):
        return f'<TeamMember {self.name} ({self.jira_id})>'
```

## Migration Strategy

### Initial Migration (Alembic)

```python
# migrations/versions/001_initial_schema.py
"""Initial schema: issues and team_members tables

Revision ID: 001_initial
Create Date: 2025-12-21
"""

def upgrade():
    # Create team_members table
    op.create_table(
        'team_members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('jira_id', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(100)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_team_members_jira_id', 'team_members', ['jira_id'], unique=True)

    # Create issues table
    op.create_table(
        'issues',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('jira_key', sa.String(20), nullable=False),
        sa.Column('summary', sa.String(500), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False),
        sa.Column('assignee_id', sa.Integer(), sa.ForeignKey('team_members.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('sla_deadline', sa.DateTime()),
        sa.Column('metadata', sa.JSON()),
    )
    op.create_index('ix_issues_jira_key', 'issues', ['jira_key'], unique=True)
    op.create_index('ix_issues_status', 'issues', ['status'])
    op.create_index('ix_issues_priority', 'issues', ['priority'])
    op.create_index('ix_issues_assignee_id', 'issues', ['assignee_id'])
    op.create_index('ix_issues_sla_deadline', 'issues', ['sla_deadline'])

def downgrade():
    op.drop_table('issues')
    op.drop_table('team_members')
```

## Data Synchronization

**Strategy**: Periodic sync from Jira to local database

1. **Fetch issues from Jira** using jira library: `jira.search_issues('project = SUPPORT ORDER BY created DESC', maxResults=10000)`
2. **Upsert issues**: For each Jira issue, check if `jira_key` exists in DB
   - If exists: UPDATE (update status, priority, assignee, updated_at)
   - If not exists: INSERT (create new Issue record)
3. **Upsert team members**: Extract unique assignees from Jira issues, upsert to team_members table
4. **Sync frequency**: Every 30 seconds (background job via APScheduler or cron)

**Alternative**: Real-time updates via Jira webhooks (more complex, deferred to future iteration)
