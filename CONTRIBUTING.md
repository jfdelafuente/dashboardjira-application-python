# Contributing to Support Team Dashboard

Thank you for your interest in contributing to the Support Team Dashboard! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)

---

## Code of Conduct

This project follows a Code of Conduct to ensure a welcoming environment for all contributors. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- PostgreSQL 12+ (for production) or SQLite (for development)
- Basic understanding of Flask, SQLAlchemy, and Jinja2

### Setting Up Development Environment

1. **Fork and Clone the Repository**

   ```bash
   git clone https://github.com/your-username/support-dashboard.git
   cd support-dashboard
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements/dev.txt
   ```

4. **Configure Environment Variables**

   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

5. **Initialize Database**

   ```bash
   flask db upgrade
   python scripts/seed_data.py --issues 50
   ```

6. **Run Tests**

   ```bash
   pytest tests/ -v
   ```

7. **Start Development Server**

   ```bash
   flask run --debug
   ```

   Open http://localhost:5000 in your browser.

---

## Development Workflow

### Branching Strategy

We follow a simplified Git Flow:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/xxx` - New features
- `bugfix/xxx` - Bug fixes
- `hotfix/xxx` - Critical production fixes

### Creating a Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Making Changes

1. Make your changes in logical, atomic commits
2. Write tests for new functionality
3. Update documentation as needed
4. Run tests and linting before committing

---

## Coding Standards

### Python Style Guide

- Follow **PEP 8** style guide
- Use **Black** for automatic formatting (line length: 88)
- Use **flake8** for linting (max line length: 100)
- Use **type hints** for function parameters and return values
- Write **docstrings** for all modules, classes, and functions (Google style)

### Running Code Quality Tools

```bash
# Format code with Black
black app/ tests/ scripts/

# Check linting with flake8
flake8 app/ --max-line-length=100

# Type checking with mypy (optional but recommended)
mypy app/services/ --ignore-missing-imports
```

### Code Organization

```
app/
├── models/          # SQLAlchemy ORM models
├── services/        # Business logic layer
├── routes/          # Flask blueprints (controllers)
├── templates/       # Jinja2 HTML templates
├── static/          # CSS, JavaScript, images
└── utils/           # Shared utilities
```

**Principles:**
- Keep business logic in `services/`
- Keep routes thin (delegate to services)
- Use blueprints for modular routes
- Separate concerns (models, services, views)

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

### Example Code Style

```python
"""
Module docstring describing the purpose.
"""

from typing import List, Dict, Optional
from app.models.issue import Issue


class IssueService:
    """Service for managing issues."""

    def get_issues_by_priority(
        self, priority: str, limit: Optional[int] = None
    ) -> List[Issue]:
        """
        Fetch issues filtered by priority.

        Args:
            priority: Priority level (Critical, High, Medium, Low)
            limit: Maximum number of issues to return (optional)

        Returns:
            List of Issue objects matching the priority

        Raises:
            ValueError: If priority is invalid
        """
        valid_priorities = ["Critical", "High", "Medium", "Low"]
        if priority not in valid_priorities:
            raise ValueError(f"Invalid priority: {priority}")

        query = Issue.query.filter(Issue.priority == priority)
        if limit:
            query = query.limit(limit)
        return query.all()
```

---

## Testing Requirements

### Test Coverage

- All new features **must** include tests
- Aim for **≥80% code coverage** overall
- Critical paths should have **100% coverage**

### Test Organization

```
tests/
├── unit/            # Unit tests (isolated, fast)
├── integration/     # Integration tests (database, multiple components)
└── conftest.py      # Shared pytest fixtures
```

### Writing Tests

**Unit Test Example:**

```python
import pytest
from app.services.kpi_service import calculate_kpis


def test_calculate_kpis_with_no_issues(db):
    """Test KPI calculation with empty database."""
    kpis = calculate_kpis()
    assert kpis["total_open"] == 0
    assert kpis["critical_issues"] == 0
    assert kpis["avg_resolution_time_hours"] == 0
```

**Integration Test Example:**

```python
def test_dashboard_displays_kpis(client, db, init_database):
    """Test dashboard renders KPI cards correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Total Open Issues" in response.data
    assert b"Critical Issues" in response.data
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_kpi_service.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run integration tests only
pytest tests/integration/ -v
```

---

## Commit Message Guidelines

Follow the **Conventional Commits** specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, config)
- `perf`: Performance improvements

### Examples

```bash
# Good commit messages
feat(kpi): add new KPI for average response time
fix(dashboard): correct calculation for overdue tickets
docs(readme): update installation instructions
test(issue-service): add tests for pagination edge cases

# Bad commit messages (avoid these)
Fixed stuff
WIP
Update code
asdfasdf
```

### Guidelines

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Limit subject line to 50 characters
- Capitalize subject line
- No period at the end of subject
- Separate subject from body with blank line
- Wrap body at 72 characters
- Explain **what** and **why**, not **how**

---

## Pull Request Process

### Before Submitting

1. ✅ All tests pass (`pytest tests/`)
2. ✅ Code coverage ≥80% (`pytest --cov=app --cov-report=term`)
3. ✅ No linting errors (`flake8 app/`)
4. ✅ Code formatted with Black (`black app/ tests/`)
5. ✅ Documentation updated (if applicable)
6. ✅ CHANGELOG.md updated (if significant change)

### Submitting a Pull Request

1. **Push your branch to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request on GitHub**

   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

3. **PR Title Format**

   ```
   [Type] Brief description (≤50 chars)
   ```

   Examples:
   - `[Feature] Add export to CSV functionality`
   - `[Bugfix] Fix pagination on last page`
   - `[Docs] Update deployment guide`

4. **PR Description Should Include:**

   - **Summary**: What does this PR do?
   - **Motivation**: Why is this change needed?
   - **Changes**: List of key changes
   - **Testing**: How was this tested?
   - **Screenshots**: If UI changes, include before/after
   - **Related Issues**: Link to issue (e.g., "Closes #123")

### PR Template Example

```markdown
## Summary
Add CSV export functionality to issue table

## Motivation
Users requested ability to export filtered issues for offline analysis

## Changes
- Added `export_to_csv()` method in `IssueService`
- Created `/api/issues/export` endpoint
- Added "Export" button to dashboard UI
- Added tests for CSV generation

## Testing
- Unit tests: `test_export_to_csv.py`
- Integration test: Verified export with 1000 issues
- Manual test: Downloaded CSV and opened in Excel

## Screenshots
![Export button](screenshots/export-button.png)

## Related Issues
Closes #42
```

### Review Process

1. **Automated Checks**: GitHub Actions CI must pass
2. **Code Review**: At least one maintainer approval required
3. **Address Feedback**: Make requested changes
4. **Squash Commits**: If many small commits, squash before merge
5. **Merge**: Maintainer will merge when approved

---

## Project Structure

### Key Directories

```
support-dashboard/
├── app/                    # Main application code
│   ├── __init__.py        # Flask app factory
│   ├── config.py          # Configuration classes
│   ├── models/            # Database models (SQLAlchemy)
│   ├── services/          # Business logic layer
│   ├── routes/            # API endpoints and views
│   ├── templates/         # Jinja2 HTML templates
│   ├── static/            # CSS, JavaScript, images
│   └── utils/             # Helper utilities
├── tests/                 # Test suite
│   ├── unit/             # Fast, isolated tests
│   ├── integration/      # Multi-component tests
│   └── conftest.py       # Shared fixtures
├── migrations/            # Database migrations (Alembic)
├── scripts/              # Utility scripts
├── requirements/         # Python dependencies
│   ├── base.txt         # Production dependencies
│   ├── dev.txt          # Development dependencies
│   └── test.txt         # Testing dependencies
├── docs/                 # Documentation
├── .github/              # GitHub Actions workflows
└── specs/                # Feature specifications
```

### Adding a New Feature

1. **Create Model** (if needed): `app/models/your_model.py`
2. **Create Service**: `app/services/your_service.py`
3. **Create Route**: `app/routes/your_route.py`
4. **Create Template**: `app/templates/your_template.html`
5. **Write Tests**: `tests/unit/test_your_service.py`
6. **Update Documentation**: README.md, docs/

---

## Questions or Issues?

- **Questions**: Open a [GitHub Discussion](https://github.com/your-org/support-dashboard/discussions)
- **Bug Reports**: Open a [GitHub Issue](https://github.com/your-org/support-dashboard/issues)
- **Feature Requests**: Open a [GitHub Issue](https://github.com/your-org/support-dashboard/issues) with label "enhancement"

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](LICENSE)).

---

**Thank you for contributing!** 🎉
