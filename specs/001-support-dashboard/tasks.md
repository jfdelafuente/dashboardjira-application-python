# Tasks: Support Team Dashboard

**Input**: Design documents from `/specs/001-support-dashboard/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD approach mandated by Constitution Principle II - tests written BEFORE implementation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US1]**, **[US2]**, **[US3]**: User story labels (maps to spec.md priorities P1, P2, P3)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with single Flask app structure:
- Application code: `app/` (models, services, routes, templates, static)
- Tests: `tests/` (contract, integration, unit)
- Migrations: `migrations/`
- Configuration: Root level (requirements/, .env, run.py, pytest.ini, etc.)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure (app/, tests/, migrations/, requirements/, static/, templates/)
- [ ] T002 Create requirements/base.txt with Flask 3.0+, SQLAlchemy 2.0+, Jinja2 3.1+, jira 3.5+, psycopg2-binary 2.9+
- [ ] T003 [P] Create requirements/dev.txt extending base.txt with pytest 7.x, pytest-flask, pytest-cov, flake8, black, mypy
- [ ] T004 [P] Create requirements/test.txt extending dev.txt with pytest plugins
- [ ] T005 Create .env.example with environment variable templates (FLASK_APP, FLASK_ENV, SECRET_KEY, DATABASE_URL, JIRA_*)
- [ ] T006 [P] Create .gitignore for Python (venv/, __pycache__/, *.pyc, .env, dashboard.db, .pytest_cache/)
- [ ] T007 [P] Create .flake8 configuration file with PEP 8 settings and line length 100
- [ ] T008 [P] Create pytest.ini with test discovery settings and coverage options
- [ ] T009 [P] Create mypy.ini for type checking configuration

**Checkpoint**: Project skeleton ready for foundational infrastructure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 Create app/__init__.py with Flask app factory pattern (create_app function)
- [ ] T011 Create app/config.py with Config classes (DevelopmentConfig, TestingConfig, ProductionConfig)
- [ ] T012 Initialize Flask-SQLAlchemy in app/__init__.py (db = SQLAlchemy())
- [ ] T013 Setup Alembic for database migrations in migrations/ directory
- [ ] T014 Create run.py application entry point that calls create_app()
- [ ] T015 [P] Create app/models/__init__.py to export all models
- [ ] T016 [P] Create app/services/__init__.py for service layer
- [ ] T017 [P] Create app/routes/__init__.py for Flask blueprints
- [ ] T018 [P] Create app/utils/__init__.py for shared utilities
- [ ] T019 Create tests/conftest.py with pytest fixtures (app, client, test_db)
- [ ] T020 [P] Create app/templates/base.html with dark theme CSS (base template with header, navigation, footer)
- [ ] T021 [P] Create app/static/css/dark-theme.css with color variables and responsive grid layout
- [ ] T022 Setup database configuration to use SQLite for testing and PostgreSQL for production in app/config.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Real-Time Support Metrics (Priority: P1) 🎯 MVP

**Goal**: Display four KPI cards (total open issues, critical issues, avg resolution time, overdue tickets) on dashboard home page

**Independent Test**: Load dashboard at http://localhost:5000 and verify all four KPI cards display with accurate calculated values

### Tests for User Story 1 (TDD - RED Phase) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T023 [P] [US1] Create tests/unit/test_models_issue.py with Issue model validation tests (status enum, priority enum, jira_key pattern, summary length)
- [ ] T024 [P] [US1] Create tests/unit/test_models_team_member.py with TeamMember model validation tests (jira_id uniqueness, name length, email format)
- [ ] T025 [P] [US1] Create tests/unit/test_kpi_service.py with KPI calculation tests (total_open, critical_issues, avg_resolution_time_hours, overdue_tickets)
- [ ] T026 [US1] Create tests/integration/test_user_story_1_kpis.py with end-to-end KPI display test (dashboard loads, KPIs visible, values accurate)

### Implementation for User Story 1 (TDD - GREEN Phase)

- [ ] T027 [P] [US1] Create app/models/team_member.py with TeamMember SQLAlchemy model (id, jira_id, name, email, timestamps, validation, workload property)
- [ ] T028 [US1] Create app/models/issue.py with Issue SQLAlchemy model (id, jira_key, summary, description, status, priority, assignee_id FK, timestamps, sla_deadline, metadata JSON, validation, is_overdue property, resolution_time_hours property)
- [ ] T029 [US1] Create Alembic migration 001_initial_schema.py for team_members and issues tables with indexes in migrations/versions/
- [ ] T030 [US1] Run migration to create database tables (flask db upgrade)
- [ ] T031 [P] [US1] Create app/services/kpi_service.py with calculate_kpis function (accepts issues list, returns dict with total_open, critical_issues, avg_resolution_time_hours, overdue_tickets)
- [ ] T032 [P] [US1] Create app/services/jira_service.py with JiraService class (get_issues method with caching, mock mode support for testing)
- [ ] T033 [US1] Create app/services/issue_service.py with IssueService class (get_all_issues, sync_from_jira, upsert_issue methods)
- [ ] T034 [US1] Create app/routes/dashboard.py Flask blueprint with index route (GET /) that renders dashboard.html
- [ ] T035 [US1] Implement dashboard index route to fetch issues, calculate KPIs, pass to template in app/routes/dashboard.py
- [ ] T036 [US1] Create app/templates/dashboard.html extending base.html with KPI cards section
- [ ] T037 [P] [US1] Create app/templates/components/kpi_card.html Jinja2 macro (accepts title, value, icon parameters)
- [ ] T038 [US1] Add four KPI cards to dashboard.html using kpi_card.html macro (Total Open, Critical Issues, Avg Resolution Time, Overdue Tickets)
- [ ] T039 [P] [US1] Style KPI cards in app/static/css/dark-theme.css (grid layout, responsive breakpoints for mobile)
- [ ] T040 [US1] Add error handling to dashboard route for Jira connection failures (display user-friendly error message)

### Verification (TDD - REFACTOR Phase)

- [ ] T041 [US1] Run tests/unit/test_kpi_service.py and verify all KPI calculations pass
- [ ] T042 [US1] Run tests/integration/test_user_story_1_kpis.py and verify end-to-end KPI display works
- [ ] T043 [US1] Verify test coverage for app/services/kpi_service.py is ≥80% (pytest --cov)
- [ ] T044 [US1] Run flake8 and black on app/services/kpi_service.py and app/models/ to ensure PEP 8 compliance

**Checkpoint**: At this point, User Story 1 (MVP) should be fully functional and independently testable. Dashboard displays accurate KPI metrics.

---

## Phase 4: User Story 2 - Visualize Issue Distribution with Charts (Priority: P2)

**Goal**: Add bar chart (status distribution) and pie chart (priority distribution) below KPI cards

**Independent Test**: Load dashboard and verify two charts render with accurate data matching database query results

### Tests for User Story 2 (TDD - RED Phase) ⚠️

- [ ] T045 [P] [US2] Create tests/unit/test_chart_service.py with chart data generation tests (get_status_distribution returns labels and data arrays, get_priority_distribution returns labels and data arrays)
- [ ] T046 [US2] Create tests/integration/test_user_story_2_charts.py with chart rendering test (dashboard charts section visible, API endpoints return correct JSON structure)

### Implementation for User Story 2 (TDD - GREEN Phase)

- [ ] T047 [P] [US2] Create app/services/chart_service.py with ChartService class (get_status_distribution, get_priority_distribution methods)
- [ ] T048 [US2] Create app/routes/api.py Flask blueprint for JSON API endpoints
- [ ] T049 [P] [US2] Implement GET /api/charts/status endpoint in app/routes/api.py (returns {"labels": [...], "data": [...]})
- [ ] T050 [P] [US2] Implement GET /api/charts/priority endpoint in app/routes/api.py (returns {"labels": [...], "data": [...]})
- [ ] T051 [US2] Add charts section to app/templates/dashboard.html with two canvas elements (status-chart, priority-chart)
- [ ] T052 [P] [US2] Create app/static/js/charts.js with Chart.js initialization (fetch data from API, render bar chart for status, render pie chart for priority)
- [ ] T053 [P] [US2] Style charts section in app/static/css/dark-theme.css (responsive layout, dark theme colors for Chart.js)
- [ ] T054 [US2] Link Chart.js 4.x CDN in app/templates/base.html (<script> tag before closing </body>)
- [ ] T055 [US2] Link app/static/js/charts.js in app/templates/dashboard.html

### Verification (TDD - REFACTOR Phase)

- [ ] T056 [US2] Run tests/unit/test_chart_service.py and verify chart data generation passes
- [ ] T057 [US2] Run tests/integration/test_user_story_2_charts.py and verify charts render correctly
- [ ] T058 [US2] Verify test coverage for app/services/chart_service.py is ≥80%
- [ ] T059 [US2] Test mobile responsiveness at 320px width (charts stack vertically, remain legible)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Dashboard displays KPIs + interactive charts.

---

## Phase 5: User Story 3 - Browse and Search Issue Details (Priority: P3)

**Goal**: Add issue table with search text field and priority filter dropdown below charts

**Independent Test**: Load dashboard, verify table displays all issues, search filters work, priority filter works

### Tests for User Story 3 (TDD - RED Phase) ⚠️

- [ ] T060 [P] [US3] Create tests/unit/test_issue_service.py with filtering tests (filter_by_text, filter_by_priority, paginate methods)
- [ ] T061 [P] [US3] Create tests/unit/test_pagination.py with pagination helper tests (calculate_pagination returns correct page/total_pages)
- [ ] T062 [US3] Create tests/integration/test_user_story_3_search.py with search/filter test (text search works, priority filter works, pagination works, combined filters work)

### Implementation for User Story 3 (TDD - GREEN Phase)

- [ ] T063 [P] [US3] Add filter methods to app/services/issue_service.py (filter_by_text, filter_by_priority, paginate)
- [ ] T064 [P] [US3] Create app/utils/pagination.py with Pagination helper class (calculate_pagination function)
- [ ] T065 [US3] Implement GET /api/issues endpoint in app/routes/api.py with query params (search, priority, page, per_page)
- [ ] T066 [US3] Create app/templates/components/issue_table.html Jinja2 template (table with 5 columns: Key, Summary, Assigned To, Priority, Status)
- [ ] T067 [US3] Add issue table section to app/templates/dashboard.html including search field and priority filter dropdown
- [ ] T068 [P] [US3] Create app/static/js/filters.js with client-side search and filter logic (event listeners for search input and priority select)
- [ ] T069 [P] [US3] Style table in app/static/css/dark-theme.css (responsive table, horizontal scroll on mobile, dark theme styling)
- [ ] T070 [US3] Add pagination controls to issue table (Previous/Next buttons, page indicator)
- [ ] T071 [US3] Link app/static/js/filters.js in app/templates/dashboard.html
- [ ] T072 [US3] Handle "Unassigned" display in table when assignee_id is NULL

### Verification (TDD - REFACTOR Phase)

- [ ] T073 [US3] Run tests/unit/test_issue_service.py and verify filtering logic passes
- [ ] T074 [US3] Run tests/integration/test_user_story_3_search.py and verify search/filter works end-to-end
- [ ] T075 [US3] Verify test coverage for app/services/issue_service.py is ≥80%
- [ ] T076 [US3] Test edge cases (zero issues, zero filter results, 1000+ issues with pagination)

**Checkpoint**: All three user stories should now be independently functional. Dashboard is feature-complete per spec.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T077 [P] Create scripts/seed_data.py to generate sample issues for testing (--issues parameter)
- [ ] T078 [P] Create scripts/test_jira_connection.py to validate Jira API credentials
- [ ] T079 [P] Add comprehensive docstrings to all modules in app/models/, app/services/, app/routes/ (Google style)
- [ ] T080 [P] Add type hints to all public functions in app/services/ and verify with mypy
- [ ] T081 Implement caching for Jira API calls in app/services/jira_service.py (functools.lru_cache with 30-second TTL)
- [ ] T082 [P] Add loading spinner to app/templates/dashboard.html for operations >1 second
- [ ] T083 [P] Add Lucide icons to KPI cards in app/templates/components/kpi_card.html
- [ ] T084 [P] Optimize database queries with eager loading (.joinedload()) for Issue → TeamMember relationship
- [ ] T085 Create production deployment guide in docs/DEPLOYMENT.md (Gunicorn + nginx + PostgreSQL setup)
- [ ] T086 [P] Add Flask-Migrate commands to README.md (flask db init, upgrade, downgrade)
- [ ] T087 Run full test suite (pytest tests/ --cov=app --cov-report=html) and verify ≥80% coverage
- [ ] T088 Run flake8 on entire app/ directory and fix all PEP 8 violations
- [ ] T089 Run black formatter on app/ and tests/ directories
- [ ] T090 Create .github/workflows/ci.yml for GitHub Actions (run tests, linting, type checking on push)
- [ ] T091 [P] Test dashboard performance with 1000 issues (page load <3s, API response <500ms)
- [ ] T092 [P] Test mobile responsiveness at 320px, 768px, 1024px widths
- [ ] T093 Verify WCAG 2.1 AA compliance (contrast ratios, keyboard navigation, ARIA labels on charts)
- [ ] T094 Run quickstart.md integration test scenarios and verify all success criteria pass

**Checkpoint**: Production-ready dashboard with ≥80% test coverage, PEP 8 compliant, performance validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion - This is MVP
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion - Can run in parallel with US1 if staffed
- **User Story 3 (Phase 5)**: Depends on Foundational phase completion - Can run in parallel with US1/US2 if staffed
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - No dependencies on other stories
- **User Story 2 (P2)**: Independent - No dependencies on other stories (but naturally builds on US1 UI)
- **User Story 3 (P3)**: Independent - No dependencies on other stories (but naturally builds on US1/US2 UI)

### Within Each User Story (TDD Flow)

1. **RED Phase**: Write tests first (T023-T026 for US1, T045-T046 for US2, T060-T062 for US3)
2. **GREEN Phase**: Implement features to make tests pass
   - Models before services (models are data layer, services use models)
   - Services before routes (routes call services)
   - Routes before templates (routes render templates)
   - Templates before static assets (templates reference CSS/JS)
3. **REFACTOR Phase**: Verify tests pass, check coverage, ensure code quality

### Parallel Opportunities

**Within Setup (Phase 1)**:
- T003, T004, T006-T009 can all run in parallel (different files, no dependencies)

**Within Foundational (Phase 2)**:
- T015-T018, T020-T021 can run in parallel (different directories, independent setups)

**Within User Story 1 Tests**:
- T023, T024, T025 can run in parallel (different test files, independent model tests)

**Within User Story 1 Implementation**:
- T027, T031, T032, T037, T039 can run in parallel (different files: team_member.py, kpi_service.py, jira_service.py, template components, CSS)

**Within User Story 2 Implementation**:
- T047, T049, T050, T052, T053 can run in parallel (chart_service.py, API routes, JS charts logic, CSS styling)

**Within User Story 3 Implementation**:
- T063, T064, T068, T069 can run in parallel (issue_service filters, pagination utils, JS filters, CSS table styling)

**Within Polish**:
- T077-T080, T082-T084, T088-T093 can run in parallel (scripts, docs, CSS, optimization, testing)

### Cross-Phase Parallelism

After Foundational phase completes:
- **Scenario 1 (Single developer)**: Implement User Stories sequentially (US1 → US2 → US3)
- **Scenario 2 (Team of 3)**: Implement all three User Stories in parallel:
  - Developer A: User Story 1 (T023-T044)
  - Developer B: User Story 2 (T045-T059)
  - Developer C: User Story 3 (T060-T076)
  - All merge and integrate independently

---

## Parallel Example: User Story 1 (MVP)

Launch all User Story 1 test tasks together (RED phase):

```bash
# Terminal 1
Task: "Create tests/unit/test_models_issue.py with Issue model validation tests"

# Terminal 2
Task: "Create tests/unit/test_models_team_member.py with TeamMember model validation tests"

# Terminal 3
Task: "Create tests/unit/test_kpi_service.py with KPI calculation tests"

# Terminal 4
Task: "Create tests/integration/test_user_story_1_kpis.py with end-to-end KPI display test"
```

After tests written and failing, launch parallelizable implementation tasks (GREEN phase):

```bash
# Terminal 1
Task: "Create app/models/team_member.py with TeamMember SQLAlchemy model"

# Terminal 2
Task: "Create app/services/kpi_service.py with calculate_kpis function"

# Terminal 3
Task: "Create app/services/jira_service.py with JiraService class"

# Terminal 4
Task: "Create app/templates/components/kpi_card.html Jinja2 macro"

# Terminal 5
Task: "Style KPI cards in app/static/css/dark-theme.css"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T022) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (T023-T044)
4. **STOP and VALIDATE**: Run integration tests, verify KPIs display correctly, test on mobile
5. Deploy MVP to staging for user feedback

**Deliverable**: Functional dashboard with real-time KPIs visible in <5 seconds

### Incremental Delivery

1. Complete Setup + Foundational (T001-T022) → Foundation ready
2. Add User Story 1 (T023-T044) → Test independently → **Deploy MVP** ✅
3. Add User Story 2 (T045-T059) → Test independently → **Deploy with charts** ✅
4. Add User Story 3 (T060-T076) → Test independently → **Deploy complete dashboard** ✅
5. Polish phase (T077-T094) → Production hardening → **Deploy to production** ✅

Each story adds value without breaking previous stories.

### Parallel Team Strategy (3 developers)

1. **Week 1**: Team completes Setup + Foundational together (T001-T022)
2. **Week 2-3**: Once Foundational is done:
   - Developer A: User Story 1 (T023-T044) - **MVP Priority**
   - Developer B: User Story 2 (T045-T059) - Charts in parallel
   - Developer C: User Story 3 (T060-T076) - Search in parallel
3. **Week 4**: Polish phase together (T077-T094)
4. Stories integrate seamlessly (independent user journeys, shared foundation)

---

## Task Count Summary

- **Setup (Phase 1)**: 9 tasks
- **Foundational (Phase 2)**: 13 tasks
- **User Story 1 (Phase 3)**: 22 tasks (4 tests + 18 implementation)
- **User Story 2 (Phase 4)**: 15 tasks (2 tests + 13 implementation)
- **User Story 3 (Phase 5)**: 17 tasks (3 tests + 14 implementation)
- **Polish (Phase 6)**: 18 tasks

**Total**: 94 tasks

**Test Tasks**: 9 test tasks (TDD approach for all 3 user stories)
**Parallel Opportunities**: 35+ tasks marked with [P] can run concurrently

---

## Notes

- **[P] marker** = Parallelizable (different files, no dependencies on incomplete tasks)
- **[US1]**, **[US2]**, **[US3]** = User story labels for traceability
- **TDD Flow**: RED (write tests) → GREEN (implement) → REFACTOR (verify coverage, code quality)
- Each user story is independently completable and testable per spec requirements
- Stop at any checkpoint to validate independently before proceeding
- Commit after completing each task or logical group
- Constitution Principle II enforced: Tests MUST be written before implementation (TDD mandatory)
