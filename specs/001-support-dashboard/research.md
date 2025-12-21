# Research: Support Team Dashboard

**Feature**: 001-support-dashboard
**Date**: 2025-12-21
**Purpose**: Document technical decisions and rationale for implementation choices

## Technology Stack Decisions

### 1. Flask vs FastAPI for Web Framework

**Decision**: Flask 3.0+

**Rationale**:
- Mature ecosystem (14+ years) with extensive documentation and community support
- Built-in Jinja2 templating for server-side rendering (perfect for dashboard UI)
- Simpler learning curve than FastAPI for team members not familiar with async/await
- Synchronous model sufficient for dashboard workload (5-50 concurrent users, <3s load time achievable)
- Proven scalability: handles 1000s of requests/second with proper deployment (Gunicorn + nginx)

**Alternatives Considered**:
- **FastAPI**: Async capabilities unnecessary for this workload. Dashboard serves pre-rendered HTML + periodic AJAX updates, not streaming real-time data. FastAPI's async overhead would add complexity without performance benefit.
- **Django**: Too heavyweight for single dashboard application. Django's admin panel, auth system, and ORM are overkill when we only need simple data visualization. Flask's minimalism aligns with Constitution Principle V (Simplicity).

### 2. SQLite (Dev) + PostgreSQL (Prod) for Data Storage

**Decision**: SQLAlchemy 2.0+ ORM with SQLite (development) and PostgreSQL 15+ (production)

**Rationale**:
- **SQLite for dev/test**: Zero-configuration database, fast test execution, perfect for local development
- **PostgreSQL for prod**: Industry-standard RDBMS, proven scalability to millions of rows, excellent JSON support for flexible issue metadata
- **SQLAlchemy ORM**: Single codebase supports both databases, abstract SQL dialect differences, provides query optimization tools
- Performance: PostgreSQL with proper indexes (status, priority, assignee columns) achieves <200ms query times for 10k+ issues

**Alternatives Considered**:
- **MySQL/MariaDB**: Similar capabilities to PostgreSQL but less robust JSON support. PostgreSQL's JSONB type ideal for storing variable Jira issue metadata.
- **MongoDB (NoSQL)**: Issue data has consistent schema (key, summary, status, priority, etc.). Relational model with foreign keys (issues → team members) is natural fit. NoSQL would sacrifice referential integrity and query performance for flexibility we don't need.
- **Direct SQL (no ORM)**: Would require maintaining separate SQL for SQLite vs PostgreSQL (different date functions, JSON operators). SQLAlchemy abstracts these differences while providing type safety.

### 3. Chart.js for Data Visualization

**Decision**: Chart.js 4.x (via CDN)

**Rationale**:
- Lightweight (60KB gzipped), renders charts entirely client-side (reduces server load)
- Supports required chart types: bar chart (status distribution), pie chart (priority distribution)
- Responsive by default (adapts to mobile screens per FR-009)
- No build step required (load from CDN, configure via JavaScript)
- Accessibility: generates semantic SVG with ARIA labels (meets WCAG 2.1 AA per Constitution Principle III)

**Alternatives Considered**:
- **D3.js**: More powerful but significantly more complex. Chart.js's declarative API (config object → chart) is simpler than D3's imperative data binding. Constitution Principle V (Simplicity) favors Chart.js.
- **Matplotlib (server-side)**: Generates static images, increases page size (200KB+ PNG vs 5KB JSON data), no interactivity (tooltips, legends). Chart.js renders from JSON data sent to client, enabling dynamic updates.
- **Plotly.js**: More features than Chart.js (3D charts, statistical plots) but larger bundle size (3MB+ uncompressed). Unnecessary for basic bar/pie charts.

### 4. Jira Python Library for Issue Tracking Integration

**Decision**: jira 3.5+ library

**Rationale**:
- Official Python client for Jira REST API (maintained by Atlassian community)
- Handles authentication (Basic, OAuth, PAT), rate limiting, pagination
- Type-safe models for Issue, User, Project objects
- Reduces custom integration code from ~3000 LOC to ~200 LOC
- Supports both Jira Cloud and Jira Server/Data Center

**Alternatives Considered**:
- **Custom REST client (requests library)**: Would require implementing authentication, pagination, rate limiting, error handling, and parsing 50+ Jira REST endpoints. DRY principle violation - jira library already provides tested implementation.
- **Generic issue tracker abstraction**: Over-engineering for initial release. User input specifically mentions "Jira", and Jira dominates issue tracker market (60%+ share). Can refactor to abstraction layer later if multiple trackers needed.

### 5. Server-Side Rendering (Jinja2) vs Client-Side SPA

**Decision**: Jinja2 templates with minimal client-side JavaScript

**Rationale**:
- Dashboard content is mostly static (KPIs, charts, table) after initial load
- Server-side rendering achieves <3 second load time target (single HTML response vs multiple API round-trips for SPA)
- Simpler architecture: Flask serves HTML directly, no build tooling (Webpack, Babel, etc.)
- SEO-friendly (not critical for internal dashboard but demonstrates good practice)
- JavaScript limited to:
  - Chart.js initialization (render bar/pie charts)
  - Search/filter interactivity (filter table rows client-side)
  - Optional: AJAX refresh every 30 seconds (update KPIs without full page reload)

**Alternatives Considered**:
- **React SPA**: Requires separate frontend build process (npm, Webpack), API-only backend, state management (Redux/Context). Adds ~50% more code and complexity for marginal benefit. Dashboard doesn't need rich interactivity of Gmail/Figma.
- **Vue.js/Svelte**: Same drawbacks as React. Server-side rendering with light JavaScript is simpler and meets all functional requirements.

### 6. Testing Strategy

**Decision**: pytest + pytest-flask + pytest-cov

**Rationale**:
- **pytest**: Python standard for testing, fixtures enable clean test setup/teardown
- **pytest-flask**: Provides Flask app context, test client for HTTP requests
- **pytest-cov**: Measures test coverage, enforces 80% minimum per Constitution Principle II
- **TDD approach**: Write tests first (Red), implement feature (Green), refactor (Refactor cycle)

**Test Categories**:
1. **Unit tests** (80%+ coverage): `tests/unit/`
   - Test services in isolation (mock Jira client, mock database)
   - Test KPI calculations (avg resolution time, overdue count)
   - Test models (Issue, TeamMember validation logic)

2. **Integration tests** (critical paths): `tests/integration/`
   - Test user story 1: Load dashboard → verify KPIs calculated correctly
   - Test user story 2: Load dashboard → verify charts render with accurate data
   - Test user story 3: Search/filter → verify table updates correctly

3. **Contract tests** (API boundaries): `tests/contract/`
   - Test Jira API integration: verify jira library returns expected Issue objects
   - Mock Jira responses, assert dashboard handles all response formats

**Alternatives Considered**:
- **unittest (stdlib)**: More verbose than pytest (setUp/tearDown vs fixtures). pytest is Python community standard.
- **Selenium/Playwright (E2E UI tests)**: Slow (minutes vs seconds for pytest), brittle (break on CSS changes). Integration tests with Flask test client sufficient for dashboard validation.

### 7. Dark Theme Implementation

**Decision**: Custom CSS (no framework like Tailwind/Bootstrap)

**Rationale**:
- Dashboard has simple layout (grid of KPI cards, charts section, table)
- CSS Grid + Flexbox handle responsive layout without framework
- Custom CSS avoids unused framework code (Bootstrap = 150KB, Tailwind = build complexity)
- Dark theme: CSS custom properties (variables) for colors, single `dark-theme.css` file

**Dark Theme Colors** (WCAG 2.1 AA contrast ratios):
- Background: `#1a1a1a` (near-black)
- Surface: `#2d2d2d` (card backgrounds)
- Primary text: `#e0e0e0` (light gray, 12:1 contrast)
- Secondary text: `#b0b0b0` (muted gray, 7:1 contrast)
- Accent: `#4a9eff` (blue for links/buttons, 4.5:1 contrast)
- Critical: `#ff4444` (red for critical issue badges, 4.8:1 contrast)

**Alternatives Considered**:
- **Tailwind CSS**: Requires PostCSS build step, generates utility classes in HTML. Adds build complexity for minimal benefit.
- **Bootstrap**: Provides dark theme but includes jQuery dependency and 150KB CSS. Overkill for simple dashboard layout.

## Best Practices and Patterns

### Flask Application Factory Pattern

**Pattern**: Use `create_app()` factory function instead of global `app` object

```python
# app/__init__.py
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    from app.routes import dashboard, api
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(api.bp)

    return app
```

**Benefit**: Enables creating multiple app instances with different configs (dev, test, prod). Critical for pytest fixtures (`@pytest.fixture def app(): return create_app('testing')`).

### Service Layer Pattern

**Pattern**: Separate business logic from routes

```python
# app/routes/dashboard.py
@bp.route('/')
def index():
    issues = issue_service.get_all_issues()
    kpis = kpi_service.calculate_kpis(issues)
    return render_template('dashboard.html', kpis=kpis, issues=issues)

# app/services/kpi_service.py
def calculate_kpis(issues):
    return {
        'total_open': len([i for i in issues if i.status != 'Done']),
        'critical': len([i for i in issues if i.priority == 'Critical']),
        # ...
    }
```

**Benefit**: Routes are thin controllers (HTTP → Service → Template). Services are pure Python functions (easy to unit test, no Flask context required).

### Database Query Optimization

**Pattern**: Add indexes on frequently queried columns

```python
# app/models/issue.py
class Issue(db.Model):
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(20), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, index=True)  # Index for filtering
    priority = db.Column(db.String(20), nullable=False, index=True)  # Index for filtering
    assignee_id = db.Column(db.Integer, db.ForeignKey('team_members.id'), index=True)
```

**Benefit**: Queries like `SELECT * FROM issues WHERE status = 'To Do'` use index scan (O(log n)) instead of full table scan (O(n)). Achieves <200ms query time for 10k+ issues.

### Caching Strategy

**Pattern**: Cache Jira API responses for 30 seconds

```python
# app/services/jira_service.py
import functools
import time

@functools.lru_cache(maxsize=1)
def get_issues_cached():
    # Cache expires after 30 seconds (implement TTL wrapper)
    return jira_client.search_issues('project = SUPPORT')
```

**Benefit**: Reduces Jira API calls from 1 per page load to 1 per 30 seconds. Acceptable staleness per spec ("update within 30 seconds"). Improves page load time from 2-3s to <1s.

## Deployment Architecture (Production)

**Stack**: Gunicorn (WSGI server) + nginx (reverse proxy) + PostgreSQL

```
Internet → nginx :80 → Gunicorn :8000 → Flask app → PostgreSQL :5432
```

**Gunicorn Configuration**:
- Workers: `(2 * CPU cores) + 1` (e.g., 4 workers on 2-core machine)
- Worker class: `sync` (synchronous workers, simpler than async for this workload)
- Timeout: 30 seconds
- Max requests per worker: 1000 (restart workers periodically to prevent memory leaks)

**nginx Configuration**:
- Reverse proxy to Gunicorn
- Serve static files directly (CSS, JS, icons) - bypass Flask for static assets
- Gzip compression for HTML/CSS/JS (reduce bandwidth by 70%)
- SSL termination (HTTPS)

**Database**:
- PostgreSQL 15+ with connection pooling (pgbouncer)
- Indexes on status, priority, assignee columns
- Vacuum and analyze scheduled weekly

## Development Workflow

1. **Environment setup**: `python -m venv venv && pip install -r requirements/dev.txt`
2. **Database migration**: `flask db upgrade` (Alembic)
3. **Run dev server**: `flask run --debug` (auto-reload on code changes)
4. **Run tests**: `pytest --cov=app --cov-report=term-missing` (check coverage)
5. **Lint code**: `flake8 app tests && mypy app` (enforce PEP 8, type hints)
6. **Format code**: `black app tests` (auto-format to PEP 8)

## Open Questions Resolved

None - all technical decisions finalized. Ready for Phase 1 (data-model.md, contracts/, quickstart.md).
