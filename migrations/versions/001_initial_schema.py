"""Initial schema: issues and team_members tables

Revision ID: 001_initial
Revises:
Create Date: 2025-12-21 22:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create team_members table
    op.create_table(
        'team_members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('jira_id', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(100), nullable=True),
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
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False),
        sa.Column('assignee_id', sa.Integer(), sa.ForeignKey('team_members.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('sla_deadline', sa.DateTime(), nullable=True),
        sa.Column('jira_metadata', sa.JSON(), nullable=True),
    )
    op.create_index('ix_issues_jira_key', 'issues', ['jira_key'], unique=True)
    op.create_index('ix_issues_status', 'issues', ['status'])
    op.create_index('ix_issues_priority', 'issues', ['priority'])
    op.create_index('ix_issues_assignee_id', 'issues', ['assignee_id'])
    op.create_index('ix_issues_sla_deadline', 'issues', ['sla_deadline'])


def downgrade():
    op.drop_table('issues')
    op.drop_table('team_members')
