"""
Test Jira API connection and credentials.

Usage:
    python scripts/test_jira_connection.py
    python scripts/test_jira_connection.py --verbose

This script validates:
- Environment variables are set
- Jira server is reachable
- Credentials are valid
- Required permissions exist
- Sample issue can be fetched
"""

import argparse
import os
import sys
from dotenv import load_dotenv


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def print_success(text):
    """Print success message."""
    print(f"[OK] {text}")


def print_error(text):
    """Print error message."""
    print(f"[ERROR] {text}")


def print_warning(text):
    """Print warning message."""
    print(f"[WARNING] {text}")


def check_environment_variables():
    """Check if required environment variables are set."""
    print_header("Step 1: Checking Environment Variables")

    # Check for server and project (always required)
    required_vars = ["JIRA_SERVER", "JIRA_PROJECT_KEY"]

    # Check authentication: either username/password OR email/token
    has_user_pass = bool(os.getenv("JIRA_USERNAME") and os.getenv("JIRA_PASSWORD"))
    has_email_token = bool(os.getenv("JIRA_EMAIL") and os.getenv("JIRA_API_TOKEN"))

    all_vars = [
        "JIRA_SERVER",
        "JIRA_USERNAME",
        "JIRA_PASSWORD",
        "JIRA_EMAIL",
        "JIRA_API_TOKEN",
        "JIRA_PROJECT_KEY",
    ]

    missing_vars = []
    for var in all_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "TOKEN" in var or "PASSWORD" in var:
                display_value = (
                    value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                )
            else:
                display_value = value
            print_success(f"{var}={display_value}")
        else:
            if var in required_vars:
                print_error(f"{var} is not set")
                missing_vars.append(var)
            else:
                print_warning(f"{var} is not set (optional)")

    # Check authentication methods
    if not has_user_pass and not has_email_token:
        print_error("No valid authentication credentials found")
        print("\nPlease set authentication variables in your .env file:")
        print("\nOption 1 - For Jira Server/Data Center (username/password):")
        print("  JIRA_USERNAME=your-username")
        print("  JIRA_PASSWORD=your-password")
        print("\nOption 2 - For Jira Cloud or Server with API token:")
        print("  JIRA_EMAIL=your-email@example.com")
        print("  JIRA_API_TOKEN=your-api-token")
        return False

    if has_user_pass:
        print_success("Using username/password authentication")
    if has_email_token:
        print_success("Using email/token authentication")

    if missing_vars:
        print_error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        return False

    return True


def test_jira_connection(verbose=False):
    """Test connection to Jira server."""
    print_header("Step 2: Testing Jira Server Connection")

    try:
        from jira import JIRA
    except ImportError:
        print_error("jira package not installed")
        print("Install with: pip install jira")
        return False

    jira_server = os.getenv("JIRA_SERVER")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    jira_username = os.getenv("JIRA_USERNAME")
    jira_password = os.getenv("JIRA_PASSWORD")

    try:
        print(f"Connecting to {jira_server}...")

        # Configure SSL verification
        verify_ssl = os.getenv("JIRA_VERIFY_SSL", "true").lower() in ("true", "1", "yes")

        jira_options = {
            "server": jira_server,
            "verify": verify_ssl,
        }

        if not verify_ssl:
            print_warning("SSL certificate verification is DISABLED")
            print_warning("This should only be used in development environments")
            # Suppress SSL warnings
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Try different authentication methods
        # For Jira Server/Data Center: username/password or API token
        # For Jira Cloud: email/API token

        auth_method = None
        if jira_username and jira_password:
            print(f"Using username/password authentication for user: {jira_username}")
            auth = (jira_username, jira_password)
            auth_method = "username/password"
        elif jira_email and jira_token:
            print(f"Using email/token authentication for user: {jira_email}")
            auth = (jira_email, jira_token)
            auth_method = "email/token"
        else:
            print_error("No valid authentication credentials found")
            print("Set either JIRA_USERNAME + JIRA_PASSWORD or JIRA_EMAIL + JIRA_API_TOKEN")
            return False

        jira = JIRA(
            options=jira_options,
            basic_auth=auth,
            timeout=60,
        )
        print_success(f"Connected to Jira server using {auth_method}: {jira_server}")

        # Test authentication
        current_user = jira.myself()
        print_success(f"Authenticated as: {current_user['displayName']}")

        if verbose:
            print(f"  Account ID: {current_user.get('accountId', 'N/A')}")
            print(f"  Email: {current_user.get('emailAddress', 'N/A')}")
            print(f"  Time Zone: {current_user.get('timeZone', 'N/A')}")

        return jira

    except Exception as e:
        print_error(f"Failed to connect to Jira: {str(e)}")
        print("\nCommon issues:")
        print("  1. Check JIRA_SERVER URL (should include https://)")
        print("  2. Verify API token is valid (regenerate if needed)")
        print("  3. Ensure network/firewall allows connection")
        print("  4. Check if Jira server is accessible")
        return False


def test_project_access(jira, verbose=False):
    """Test access to specified project."""
    print_header("Step 3: Testing Project Access")

    project_key = os.getenv("JIRA_PROJECT_KEY")

    try:
        project = jira.project(project_key)
        print_success(f"Project found: {project.name} ({project_key})")

        if verbose:
            print(f"  Project ID: {project.id}")
            print(f"  Project Type: {project.projectTypeKey}")
            print(
                f"  Lead: {project.lead.displayName if hasattr(project, 'lead') else 'N/A'}"
            )

        return True

    except Exception as e:
        print_error(f"Cannot access project '{project_key}': {str(e)}")
        print("\nPossible issues:")
        print("  1. Project key is incorrect")
        print("  2. User doesn't have permission to view project")
        print("  3. Project doesn't exist")
        return False


def test_issue_query(jira, verbose=False):
    """Test querying issues from project."""
    print_header("Step 4: Testing Issue Query")

    project_key = os.getenv("JIRA_PROJECT_KEY")

    try:
        # Query for issues
        jql = f'project = "{project_key}" ORDER BY created DESC'
        issues = jira.search_issues(jql, maxResults=5)

        print_success(f"Query successful: Found {len(issues)} issues (limited to 5)")

        if verbose and issues:
            print("\nSample issues:")
            for issue in issues[:3]:
                print(f"  - {issue.key}: {issue.fields.summary[:60]}...")
                print(f"    Status: {issue.fields.status.name}")
                print(
                    f"    Priority: {issue.fields.priority.name if hasattr(issue.fields, 'priority') and issue.fields.priority else 'None'}"
                )

        if not issues:
            print_warning(f"No issues found in project '{project_key}'")
            print(
                "This is normal for new projects. You can create test issues in Jira."
            )

        return True

    except Exception as e:
        print_error(f"Failed to query issues: {str(e)}")
        print("\nPossible issues:")
        print("  1. Insufficient permissions to search issues")
        print("  2. JQL syntax error")
        return False


def test_field_access(jira, verbose=False):
    """Test access to required fields."""
    print_header("Step 5: Testing Field Access")

    project_key = os.getenv("JIRA_PROJECT_KEY")

    try:
        jql = f'project = "{project_key}" ORDER BY created DESC'
        issues = jira.search_issues(jql, maxResults=1)

        if not issues:
            print_warning("No issues available to test field access")
            print("Create a test issue in Jira to validate all fields")
            return True

        issue = issues[0]
        required_fields = ["summary", "status", "created"]
        optional_fields = ["priority", "assignee", "description", "resolutiondate"]

        print("Testing required fields:")
        for field in required_fields:
            if hasattr(issue.fields, field):
                value = getattr(issue.fields, field)
                if value:
                    print_success(f"  {field}: accessible")
                else:
                    print_warning(f"  {field}: accessible but empty")
            else:
                print_error(f"  {field}: not accessible")
                return False

        if verbose:
            print("\nTesting optional fields:")
            for field in optional_fields:
                if hasattr(issue.fields, field):
                    value = getattr(issue.fields, field)
                    if value:
                        print_success(f"  {field}: accessible")
                    else:
                        print_warning(f"  {field}: accessible but empty")
                else:
                    print_warning(f"  {field}: not available (will use defaults)")

        print_success("All required fields are accessible")
        return True

    except Exception as e:
        print_error(f"Failed to test field access: {str(e)}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test Jira API connection and credentials"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    print_header("Jira Connection Test")
    print("This script will validate your Jira API configuration")

    # Run tests
    success = True

    if not check_environment_variables():
        success = False
    else:
        jira = test_jira_connection(args.verbose)
        if not jira:
            success = False
        else:
            if not test_project_access(jira, args.verbose):
                success = False
            else:
                if not test_issue_query(jira, args.verbose):
                    success = False
                else:
                    test_field_access(jira, args.verbose)

    # Print final result
    print_header("Test Results")
    if success:
        print_success("All tests passed! Your Jira configuration is correct.")
        print("\nYou can now run the application:")
        print("  flask run")
        print("\nOr sync data from Jira:")
        print("  flask shell")
        print("  >>> from app.services.issue_service import IssueService")
        print("  >>> service = IssueService()")
        print("  >>> service.sync_from_jira()")
        sys.exit(0)
    else:
        print_error("Some tests failed. Please fix the issues above.")
        print("\nFor help, see:")
        print(
            "  - Jira API documentation: https://developer.atlassian.com/cloud/jira/platform/rest/v3/"
        )
        print(
            "  - API token creation: https://id.atlassian.com/manage-profile/security/api-tokens"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
