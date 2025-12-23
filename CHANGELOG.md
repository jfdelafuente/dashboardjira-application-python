# Changelog

All notable changes to the Support Team Dashboard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### To Be Added
- Full Jira API integration (currently using mock data)
- User authentication and authorization
- Real-time updates via WebSockets
- Export functionality (CSV, Excel)
- Advanced filtering (by status, assignee, date ranges)
- Sortable table columns
- Issue detail modal/page

---

## [1.0.0] - 2025-12-21

### Added - Initial Release

#### Phase 1: Foundation
- Project structure setup with Flask app factory pattern
- SQLAlchemy ORM integration
- Alembic database migrations
- pytest test framework with fixtures
- Development, testing, and production configurations
- Dark theme CSS with responsive layout
- Environment variable configuration

#### Phase 2: User Story 1 - KPI Dashboard
- **KPI Calculation Service** (`app/services/kpi_service.py`)
  - Total open issues counter
  - Critical issues counter
  - Average resolution time calculator
  - Overdue tickets counter
- **Dashboard Route** (`app/routes/dashboard.py`)
  - Main dashboard view at `/`
  - KPI data rendering
- **KPI Cards Component** (`app/templates/components/kpi_card.html`)
  - Reusable Jinja2 macro
  - Responsive grid layout (4 columns → 2 columns → 1 column)
- **Tests**
  - 10 unit tests for KPI calculations
  - 8 integration tests for dashboard rendering
  - 100% coverage for kpi_service.py

#### Phase 3: Data Models
- **Issue Model** (`app/models/issue.py`)
  - Fields: jira_key, summary, description, status, priority, assignee_id, timestamps, sla_deadline
  - Validation: status enum, priority enum, jira_key pattern, summary length
  - Properties: is_overdue, resolution_time_hours
- **TeamMember Model** (`app/models/team_member.py`)
  - Fields: jira_id, name, email, timestamps
  - Validation: name length, email format, jira_id uniqueness
  - Property: workload (count of assigned open issues)
- **Database Migration** (`migrations/versions/001_initial_schema.py`)
  - team_members table with indexes
  - issues table with foreign key to team_members
  - Indexes on status, priority, assignee_id, created_at, sla_deadline

#### Phase 4: User Story 2 - Charts
- **Chart Data Service** (`app/services/chart_service.py`)
  - Status distribution (To Do, In Progress, Done)
  - Priority distribution for open issues (Critical, High, Medium, Low)
- **API Endpoints** (`app/routes/api.py`)
  - GET `/api/kpis` - KPI metrics
  - GET `/api/charts/status` - Status distribution data
  - GET `/api/charts/priority` - Priority distribution data
- **Chart.js Integration** (`app/static/js/charts.js`)
  - Bar chart for status distribution
  - Pie chart for priority distribution
  - Dark theme color scheme
  - Responsive canvas sizing
- **Tests**
  - 10 unit tests for chart data generation
  - 10 integration tests for chart rendering
  - 100% coverage for chart_service.py

#### Phase 5: User Story 3 - Browse and Search
- **Pagination Utility** (`app/utils/pagination.py`)
  - calculate_pagination() helper function
  - Metadata: page, per_page, total_items, total_pages, has_prev, has_next
- **Extended Issue Service** (`app/services/issue_service.py`)
  - filter_by_text() - Case-insensitive search in jira_key and summary
  - filter_by_priority() - Filter by priority value
  - get_paginated_issues() - Combined filtering and pagination with eager loading
- **API Endpoint** (`app/routes/api.py`)
  - GET `/api/issues` - Paginated and filtered issues
  - Query params: search, priority, page, per_page
- **Issue Table Component** (`app/templates/components/issue_table.html`)
  - Reusable table macro with 5 columns
  - Responsive design with horizontal scroll on mobile
- **Client-Side Filtering** (`app/static/js/filters.js`)
  - Debounced search input (300ms delay)
  - Priority filter dropdown
  - Dynamic table rendering with XSS protection
  - Pagination controls (previous/next buttons)
- **Styling** (`app/static/css/dark-theme.css`)
  - Table styling with priority/status badges
  - Responsive breakpoints (768px, 480px, 320px)
  - Search and filter controls styling
- **Tests**
  - 9 unit tests for filtering logic
  - 10 unit tests for pagination
  - 14 integration tests for search/filter functionality
  - 100% coverage for pagination.py

#### Phase 6: Polish & Production Readiness
- **Utility Scripts**
  - `scripts/seed_data.py` - Generate sample test data (supports --issues and --clear)
  - `scripts/test_jira_connection.py` - Validate Jira API credentials
- **Documentation**
  - Comprehensive docstrings (Google style) for all service modules
  - Type hints for main service functions
  - `docs/DEPLOYMENT.md` - Production deployment guide (Gunicorn + nginx + PostgreSQL)
  - README.md updated with Flask-Migrate commands and utility scripts
  - CONTRIBUTING.md with development guidelines
  - CHANGELOG.md (this file)
  - CODE_OF_CONDUCT.md
- **Performance Optimizations**
  - Eager loading with .joinedload() for Issue → TeamMember relationship
  - Database query optimization in get_paginated_issues()
- **CI/CD**
  - GitHub Actions workflow (`.github/workflows/ci.yml`)
  - Multi-version Python testing (3.10, 3.11, 3.12)
  - Automated linting (flake8)
  - Code formatting checks (black)
  - Type checking (mypy)
  - Test coverage reporting (Codecov)
  - Security scanning (safety, bandit)
- **Quality Assurance**
  - 95 tests passing (62 unit + 33 integration)
  - 85% test coverage (exceeds 80% requirement)
  - Zero flake8 violations
  - Black formatting applied to all Python files

### Technical Stack

- **Backend**: Flask 3.0, SQLAlchemy 2.0, Alembic
- **Database**: SQLite (dev), PostgreSQL 12+ (prod)
- **Frontend**: Jinja2, Chart.js 4.x, Vanilla JavaScript
- **Testing**: pytest 7.x, pytest-flask, pytest-cov
- **Code Quality**: flake8, black, mypy
- **Integration**: Jira API 3.5 (mock mode supported)

### Test Coverage by Module

- app/config.py: 100%
- app/utils/pagination.py: 100%
- app/services/kpi_service.py: 100%
- app/services/chart_service.py: 100%
- app/routes/api.py: 100%
- app/models/issue.py: 96%
- app/models/team_member.py: 96%
- **Overall: 85%**

### Known Limitations

- Jira API integration uses mock data (real integration pending)
- No user authentication (assumes internal trusted network)
- No real-time updates (manual refresh required)
- No advanced filtering (by status, assignee, date ranges)

---

## Version History

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)

### Release Notes

- **1.0.0** (2025-12-21): Initial production-ready release with all core features

---

## How to Update This File

When making changes, add entries under `[Unreleased]` section using these categories:

- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security fixes

Example:

```markdown
## [Unreleased]

### Added
- Export to CSV functionality for issue table

### Fixed
- Pagination bug on last page with uneven number of items
```

When releasing a new version, move items from `[Unreleased]` to a new version section:

```markdown
## [1.1.0] - 2025-01-15

### Added
- Export to CSV functionality for issue table

### Fixed
- Pagination bug on last page with uneven number of items
```

---

**Note**: For detailed commit history, see [GitHub Commits](https://github.com/your-org/support-dashboard/commits).
