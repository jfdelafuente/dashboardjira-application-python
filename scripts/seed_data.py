"""
Seed data script for generating sample issues.

Usage:
    python scripts/seed_data.py --issues 50
    python scripts/seed_data.py --issues 1000 --clear

Options:
    --issues: Number of issues to generate (default: 50)
    --clear: Clear existing data before seeding
"""

import argparse
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models.issue import Issue
from app.models.team_member import TeamMember


# Sample data pools
JIRA_KEYS = ["SUP", "BUG", "FEAT", "TECH", "HELP"]

SUMMARIES = [
    "Login page not loading",
    "Cannot reset password",
    "Dashboard shows incorrect data",
    "API timeout on large requests",
    "Mobile app crashes on startup",
    "Email notifications not working",
    "Search functionality slow",
    "Export to PDF fails",
    "Payment processing error",
    "User profile update fails",
    "Database connection timeout",
    "Memory leak in background worker",
    "File upload size limit exceeded",
    "Session expires too quickly",
    "Chart rendering performance issue",
    "Filter dropdown not updating",
    "Pagination breaks on last page",
    "Dark mode toggle not saving",
    "Responsive layout issues on tablet",
    "CORS error on API endpoint",
]

DESCRIPTIONS = [
    "Users are reporting issues with this functionality.",
    "This is causing major problems for customers.",
    "We need to investigate this urgently.",
    "Performance degradation observed under load.",
    "Edge case discovered during testing.",
    "Security vulnerability reported by audit.",
    "Customer escalation from enterprise client.",
    "Feature request from product team.",
    "Technical debt that needs addressing.",
    "Bug introduced in last deployment.",
]

STATUSES = ["To Do", "In Progress", "Done"]
PRIORITIES = ["Critical", "High", "Medium", "Low"]

TEAM_MEMBERS = [
    ("john.doe@example.com", "John Doe", "jira_user_001"),
    ("jane.smith@example.com", "Jane Smith", "jira_user_002"),
    ("bob.wilson@example.com", "Bob Wilson", "jira_user_003"),
    ("alice.johnson@example.com", "Alice Johnson", "jira_user_004"),
    ("charlie.brown@example.com", "Charlie Brown", "jira_user_005"),
]


def clear_data():
    """Clear all existing issues and team members."""
    print("Clearing existing data...")
    Issue.query.delete()
    TeamMember.query.delete()
    db.session.commit()
    print("[OK] Data cleared")


def create_team_members():
    """Create sample team members."""
    print("Creating team members...")
    members = []

    for email, name, jira_id in TEAM_MEMBERS:
        member = TeamMember(email=email, name=name, jira_id=jira_id)
        db.session.add(member)
        members.append(member)

    db.session.commit()
    print(f"[OK] Created {len(members)} team members")
    return members


def generate_issue(issue_number, team_members):
    """Generate a single random issue."""
    prefix = random.choice(JIRA_KEYS)
    jira_key = f"{prefix}-{issue_number:05d}"
    summary = random.choice(SUMMARIES)
    description = random.choice(DESCRIPTIONS)
    status = random.choice(STATUSES)
    priority = random.choice(PRIORITIES)

    # 20% chance of being unassigned
    assignee = random.choice(team_members) if random.random() > 0.2 else None

    # Random creation date in last 90 days
    created_at = datetime.utcnow() - timedelta(days=random.randint(0, 90))

    # Resolved issues have resolution time
    resolved_at = None
    if status == "Done":
        resolved_at = created_at + timedelta(
            hours=random.randint(1, 72)  # 1-72 hours to resolve
        )

    # SLA deadline (2-7 days from creation)
    sla_deadline = created_at + timedelta(days=random.randint(2, 7))

    # Critical issues have shorter SLA
    if priority == "Critical":
        sla_deadline = created_at + timedelta(hours=random.randint(4, 24))

    issue = Issue(
        jira_key=jira_key,
        summary=summary,
        description=description,
        status=status,
        priority=priority,
        assignee_id=assignee.id if assignee else None,
        created_at=created_at,
        resolved_at=resolved_at,
        sla_deadline=sla_deadline,
    )

    return issue


def seed_issues(count):
    """Seed the database with sample issues."""
    print(f"Generating {count} sample issues...")

    # Create team members first
    team_members = create_team_members()

    # Generate issues in batches for better performance
    batch_size = 100
    issues_created = 0

    for i in range(0, count, batch_size):
        batch = []
        for j in range(min(batch_size, count - i)):
            issue = generate_issue(i + j + 1, team_members)
            batch.append(issue)

        db.session.bulk_save_objects(batch)
        db.session.commit()
        issues_created += len(batch)

        if issues_created % 100 == 0:
            print(f"  Created {issues_created}/{count} issues...")

    print(f"[OK] Created {issues_created} issues")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Seed database with sample issues for testing"
    )
    parser.add_argument(
        "--issues",
        type=int,
        default=50,
        help="Number of issues to generate (default: 50)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before seeding",
    )

    args = parser.parse_args()

    # Create Flask app context
    app = create_app()

    with app.app_context():
        print("=" * 60)
        print("Support Dashboard - Seed Data Script")
        print("=" * 60)

        if args.clear:
            clear_data()

        seed_issues(args.issues)

        # Print summary
        total_issues = Issue.query.count()
        total_members = TeamMember.query.count()
        open_issues = Issue.query.filter(Issue.status != "Done").count()
        critical_issues = Issue.query.filter(Issue.priority == "Critical").count()

        print("\n" + "=" * 60)
        print("Seeding Complete!")
        print("=" * 60)
        print(f"Total Issues:     {total_issues}")
        print(f"Team Members:     {total_members}")
        print(f"Open Issues:      {open_issues}")
        print(f"Critical Issues:  {critical_issues}")
        print("=" * 60)


if __name__ == "__main__":
    main()
