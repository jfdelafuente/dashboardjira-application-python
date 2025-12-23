# Implementation Plan: Support Team Dashboard

**Branch**: `001-support-dashboard` | **Date**: 2025-12-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-support-dashboard/spec.md`

## Summary

Build a responsive web dashboard that visualizes issue tracking data for support teams. The dashboard will display real-time KPIs (open issues, critical issues, avg resolution time, overdue tickets), interactive charts (status distribution bar chart, priority pie chart), and a searchable/filterable data table. Uses Flask for backend API, Jinja2 templates for server-side rendering, SQLAlchemy ORM with SQLite (dev) and PostgreSQL (prod), and Chart.js for client-side visualizations. Focus on <3 second load time, mobile responsiveness (320px min width), and dark mode UI.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Flask 3.0+, SQLAlchemy 2.0+, Jinja2 3.1+, Chart.js 4.x (CDN), Jira Python library (jira 3.5+)
**Storage**: SQLite (development/testing), PostgreSQL 15+ (production)
**Testing**: pytest 7.x, pytest-flask, pytest-cov
**Target Platform**: Web (modern browsers: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (single Flask app with server-side rendering + minimal client-side JS)
**Performance Goals**: <3 second page load, <500ms API response time p95, support 50 concurrent users
**Constraints**: <200ms database query time, <100MB memory footprint per worker, mobile-responsive (320px-2560px width)
**Scale/Scope**: 5-50 concurrent users, 1k-10k issues displayed, ~2000 LOC total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Planning Phase Gates

✅ **Technical stack choices align with performance requirements**
- Flask + SQLAlchemy supports <500ms API response (lightweight framework)
- Chart.js renders client-side (offloads server)
- Database indexes on status, priority, assignee columns for <200ms queries
- SQLite for dev (zero-config), PostgreSQL for prod (proven scalability to 10k+ issues)

✅ **Architecture supports testability**
- Clear layer separation: Routes → Services → Data Access (SQLAlchemy models)
- Dependency injection for Jira client (mockable in tests)
- pytest fixtures for test database setup/teardown
- Contract tests for Jira API integration
- Integration tests for end-to-end user journeys

❌ **Complexity violations requiring justification** (see Complexity Tracking below)

### Constitution Principle Alignment

**I. Code Quality Standards**
- Python style: PEP 8 (enforced by flake8, black formatter)
- Type hints required for all public functions (checked by mypy)
- Docstrings for all modules, classes, and public functions (Google style)
- No duplication: shared logic in services/ and utils/

**II. Testing Discipline**
- TDD approach: Write tests → Red → Green → Refactor
- Unit test coverage target: 80% minimum
- Integration tests for all three user stories (P1, P2, P3)
- Contract tests for Jira API integration

**III. User Experience Consistency**
- Consistent dark theme across all pages
- Error messages: "Unable to load issue data. Please check your connection." (user-friendly)
- Mobile-responsive layout (CSS Grid + Flexbox)
- Loading spinners for operations >1 second

**IV. Performance Requirements**
- Database query optimization: indexes on frequently queried columns
- Caching strategy: Cache Jira API responses for 30 seconds (acceptable staleness per spec)
- Pagination: 50 issues per page (prevents large DOM rendering)

## Project Structure

### Documentation (this feature)

```text
specs/001-support-dashboard/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api.yaml         # OpenAPI 3.0 specification for REST endpoints
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app/
├── __init__.py          # Flask app factory
├── config.py            # Configuration (dev/test/prod environments)
├── models/              # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── issue.py         # Issue model
│   └── team_member.py   # Team Member model
├── services/            # Business logic layer
│   ├── __init__.py
│   ├── jira_service.py  # Jira API integration
│   ├── kpi_service.py   # KPI calculation logic
│   └── issue_service.py # Issue data operations
├── routes/              # Flask blueprints (controllers)
│   ├── __init__.py
│   ├── dashboard.py     # Main dashboard route
│   └── api.py           # JSON API endpoints (for AJAX updates)
├── templates/           # Jinja2 HTML templates
│   ├── base.html        # Base template with dark theme CSS
│   ├── dashboard.html   # Main dashboard page
│   └── components/      # Reusable template components
│       ├── kpi_card.html
│       ├── charts.html
│       └── issue_table.html
├── static/              # Static assets
│   ├── css/
│   │   └── dark-theme.css
│   ├── js/
│   │   ├── charts.js    # Chart.js initialization
│   │   └── filters.js   # Search and filter logic
│   └── icons/           # Lucide icons (SVG)
└── utils/               # Shared utilities
    ├── __init__.py
    └── pagination.py    # Pagination helper

tests/
├── conftest.py          # pytest fixtures (test DB, mock Jira client)
├── contract/            # Contract tests
│   └── test_jira_api.py
├── integration/         # End-to-end tests
│   ├── test_user_story_1_kpis.py
│   ├── test_user_story_2_charts.py
│   └── test_user_story_3_search.py
└── unit/                # Unit tests
    ├── test_kpi_service.py
    ├── test_issue_service.py
    └── test_models.py

migrations/              # Alembic database migrations
└── versions/

requirements/
├── base.txt             # Production dependencies
├── dev.txt              # Development dependencies (includes base.txt)
└── test.txt             # Test dependencies (includes dev.txt)

run.py                   # Application entry point
.env.example             # Example environment variables
.flake8                  # Flake8 configuration
pytest.ini               # pytest configuration
mypy.ini                 # mypy type checking configuration
```

**Structure Decision**: Selected "Web application" structure adapted for single Flask app. Since this is a dashboard (not a complex SPA), server-side rendering with Jinja2 is simpler than separate frontend/backend. Client-side JavaScript limited to Chart.js and search/filter interactivity. This aligns with Constitution Principle V (Simplicity) - avoid unnecessary complexity of separate React/Vue frontend when Jinja2 templates suffice.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Using Chart.js library (client-side dependency) | Spec requires bar chart and pie chart visualizations. Flask alone cannot render interactive charts. | Server-side chart generation (e.g., matplotlib) would require sending images, increasing page size and reducing interactivity. Chart.js is industry standard (7M+ weekly npm downloads) and renders efficiently in browser. |
| SQLAlchemy ORM layer | Need to support both SQLite (dev) and PostgreSQL (prod) with single codebase. ORM abstracts database differences. | Direct SQL queries would require maintaining separate SQL dialects for SQLite vs PostgreSQL, violating DRY principle and increasing maintenance burden. SQLAlchemy is Python standard for database abstraction. |
| Jira Python library | Spec requires integration with "external issue tracking system". Jira is the most common issue tracker for support teams (mentioned in original user input). | Writing custom Jira REST API client would duplicate ~3000 LOC that jira library already provides, tested, and maintained. Using mock data is acceptable for MVP but plan must account for real integration. |

**Justification Summary**: All three "complexity" additions are industry-standard libraries solving problems where simpler alternatives would violate DRY principle or require significantly more custom code. Chart.js, SQLAlchemy, and Jira library are the simplest solutions that satisfy Constitution's Correctness + Testability + Performance + Simplicity requirements.
