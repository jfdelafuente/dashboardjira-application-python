# Quickstart Guide: Support Team Dashboard

**Feature**: 001-support-dashboard
**Date**: 2025-12-21
**Purpose**: Integration test scenarios and validation checklist

## Prerequisites

1. Python 3.11+ installed
2. PostgreSQL 15+ installed and running (or SQLite for dev mode)
3. Jira account with API access (or use mock data for testing)

## Setup Instructions

### 1. Environment Setup

```bash
# Clone repository
cd /path/to/project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt
```

### 2. Configure Environment Variables

Create `.env` file in project root:

```bash
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///dashboard.db  # For development
# DATABASE_URL=postgresql://user:pass@localhost:5432/dashboard  # For production

# Jira Integration
JIRA_SERVER=https://your-company.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_PROJECT_KEY=SUPPORT

# Optional: Mock Data Mode (for testing without Jira)
USE_MOCK_DATA=True
```

### 3. Initialize Database

```bash
# Create database tables
flask db upgrade

# (Optional) Seed with sample data
python scripts/seed_data.py
```

### 4. Run Development Server

```bash
flask run --debug
# Server starts at http://localhost:5000
```

## Integration Test Scenarios

### User Story 1: View Real-Time Support Metrics (P1)

**Objective**: Verify KPI cards display correctly with accurate calculations

**Test Steps**:

1. **Setup**: Ensure database has at least 10 sample issues with varying statuses and priorities
   ```bash
   python scripts/seed_data.py --issues=50
   ```

2. **Action**: Open browser and navigate to `http://localhost:5000`

3. **Verify**:
   - ✅ Page loads within 3 seconds
   - ✅ Four KPI cards are visible without scrolling
   - ✅ **Total Open Issues** card shows count of issues with status != "Done"
   - ✅ **Critical Issues** card shows count of issues with priority = "Critical"
   - ✅ **Avg Resolution Time** card shows average hours (e.g., "18.5 hours" or "N/A" if no resolved issues)
   - ✅ **Overdue Tickets** card shows count of issues past SLA deadline

4. **Validation Query** (check accuracy):
   ```sql
   -- Total open issues
   SELECT COUNT(*) FROM issues WHERE status != 'Done';

   -- Critical issues
   SELECT COUNT(*) FROM issues WHERE priority = 'Critical';

   -- Average resolution time (hours)
   SELECT AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600)
   FROM issues WHERE resolved_at IS NOT NULL;

   -- Overdue tickets
   SELECT COUNT(*) FROM issues
   WHERE status != 'Done' AND sla_deadline < NOW();
   ```

5. **Dynamic Update Test**:
   - Create a new issue in Jira (or via API)
   - Wait 30 seconds (sync interval)
   - Refresh dashboard
   - ✅ Verify KPI cards update to reflect new issue

**Expected Result**: All KPI cards display accurate, up-to-date metrics

---

### User Story 2: Visualize Issue Distribution with Charts (P2)

**Objective**: Verify bar chart and pie chart render correctly with accurate data

**Test Steps**:

1. **Action**: Scroll to charts section on dashboard

2. **Verify Bar Chart (Status Distribution)**:
   - ✅ Chart title: "Issues by Status"
   - ✅ X-axis labels: "To Do", "In Progress", "Done"
   - ✅ Y-axis shows issue counts
   - ✅ Bars display correct heights (proportional to issue counts)
   - ✅ Tooltip appears on hover showing exact count

3. **Verify Pie Chart (Priority Distribution)**:
   - ✅ Chart title: "Priority Distribution"
   - ✅ Legend shows: "Critical", "High", "Medium", "Low"
   - ✅ Pie slices sized proportionally to issue counts
   - ✅ Tooltip appears on hover showing percentage and count

4. **Validation API Call**:
   ```bash
   # Test status distribution endpoint
   curl http://localhost:5000/api/charts/status
   # Expected: {"labels": ["To Do", "In Progress", "Done"], "data": [15, 20, 12]}

   # Test priority distribution endpoint
   curl http://localhost:5000/api/charts/priority
   # Expected: {"labels": ["Critical", "High", "Medium", "Low"], "data": [5, 12, 20, 10]}
   ```

5. **Mobile Responsive Test**:
   - Resize browser window to 320px width
   - ✅ Verify charts stack vertically (one per row)
   - ✅ Verify charts remain legible and interactive

**Expected Result**: Both charts render accurately and are responsive on all screen sizes

---

### User Story 3: Browse and Search Issue Details (P3)

**Objective**: Verify issue table displays correctly and filters work

**Test Steps**:

1. **Action**: Scroll to issue table section

2. **Verify Table Structure**:
   - ✅ Table has 5 columns: Key, Summary, Assigned To, Priority, Status
   - ✅ All issues from database are displayed (up to 50 per page)
   - ✅ Pagination controls appear if >50 issues exist

3. **Text Search Test**:
   - **Setup**: Ensure database has issue with jira_key "SUP-1234" and summary containing "authentication"
   - **Action**: Type "auth" in search field
   - **Verify**:
     - ✅ Table filters to show only issues where key or summary contains "auth"
     - ✅ Issue "SUP-1234" is visible
     - ✅ Other issues are hidden

4. **Priority Filter Test**:
   - **Action**: Select "Critical" from priority dropdown
   - **Verify**:
     - ✅ Table filters to show only issues with priority = "Critical"
     - ✅ Count matches KPI card "Critical Issues" count

5. **Combined Filter Test**:
   - **Action**: Keep priority filter = "Critical", type "login" in search
   - **Verify**:
     - ✅ Table shows only Critical issues with "login" in key or summary
     - ✅ If no matches, displays "No issues match your filters" message

6. **Clear Filters Test**:
   - **Action**: Clear search field and reset priority filter to "All"
   - **Verify**:
     - ✅ Table shows all issues again
     - ✅ Pagination resets to page 1

7. **Pagination Test** (if >50 issues):
   - **Setup**: Ensure database has >50 issues
   - **Verify**:
     - ✅ Table shows 50 issues on page 1
     - ✅ Pagination controls show "Page 1 of N"
     - ✅ Click "Next" → page 2 loads with next 50 issues
     - ✅ URL updates to `?page=2`

8. **Unassigned Issues Test**:
   - **Setup**: Create issue with `assignee_id = NULL`
   - **Verify**:
     - ✅ Assigned To column shows "Unassigned" for that issue

**Expected Result**: Table displays all issues correctly, filters work as expected, pagination functions properly

---

## Edge Case Validation

### Zero Issues in Database

**Test Steps**:

1. Clear database: `flask db downgrade base && flask db upgrade`
2. Navigate to dashboard
3. **Verify**:
   - ✅ KPI cards show: 0, 0, "N/A", 0
   - ✅ Charts show empty state or "No data available"
   - ✅ Table shows "No issues found" message
   - ✅ No errors in console

### Jira Connection Failure

**Test Steps**:

1. Set invalid Jira credentials in `.env`
2. Restart Flask server
3. Navigate to dashboard
4. **Verify**:
   - ✅ Error message displays: "Unable to load issue data. Please check your connection and try again."
   - ✅ Page doesn't crash (graceful error handling)
   - ✅ Error logged to console with stack trace

### Mobile Device (320px Width)

**Test Steps**:

1. Open Chrome DevTools
2. Set device to "iPhone SE" (375x667) or custom 320px width
3. Navigate to dashboard
4. **Verify**:
   - ✅ KPI cards stack vertically (one per row)
   - ✅ Charts stack vertically (one per row)
   - ✅ Table is horizontally scrollable
   - ✅ All text is legible (no truncation)
   - ✅ Touch targets are ≥44x44px (buttons, dropdowns)

### Performance with 1000+ Issues

**Test Steps**:

1. Seed database with 1000 issues: `python scripts/seed_data.py --issues=1000`
2. Navigate to dashboard
3. **Verify**:
   - ✅ Page load time <3 seconds
   - ✅ API response time <500ms (check Network tab)
   - ✅ Database query time <200ms (check Flask debug toolbar)
   - ✅ Pagination shows 20 pages (1000 issues / 50 per page)

---

## Automated Integration Tests

Run full integration test suite:

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific user story test
pytest tests/integration/test_user_story_1_kpis.py -v

# Run with coverage report
pytest tests/integration/ --cov=app --cov-report=html
```

**Expected Output**:

```
tests/integration/test_user_story_1_kpis.py::test_kpi_cards_display ✓
tests/integration/test_user_story_1_kpis.py::test_kpi_accuracy ✓
tests/integration/test_user_story_2_charts.py::test_status_chart_renders ✓
tests/integration/test_user_story_2_charts.py::test_priority_chart_renders ✓
tests/integration/test_user_story_3_search.py::test_text_search_filters ✓
tests/integration/test_user_story_3_search.py::test_priority_filter ✓
tests/integration/test_user_story_3_search.py::test_pagination ✓

==================== 7 passed in 2.34s ====================
```

---

## Success Criteria Validation

After completing all test scenarios, verify against spec success criteria:

- ✅ **SC-001**: Support team members can assess workload in <5 seconds (page load + KPI scan)
- ✅ **SC-002**: Managers identify status distribution in <10 seconds (charts visible on first scroll)
- ✅ **SC-003**: Users locate specific issue in <15 seconds (search + filter)
- ✅ **SC-004**: Dashboard loads in <3 seconds on broadband (measure with Chrome DevTools)
- ✅ **SC-005**: Dashboard usable on 320px width mobile (test with responsive mode)
- ✅ **SC-006**: 90% user satisfaction (conduct survey after 2-week pilot)
- ✅ **SC-007**: 30% reduction in time checking Jira (measure via usage analytics)
- ✅ **SC-008**: Data accuracy (validate against direct Jira queries)

---

## Troubleshooting

### Issue: Dashboard shows "Unable to load issue data"

**Solution**:
1. Check Jira credentials in `.env`
2. Test Jira connection: `python scripts/test_jira_connection.py`
3. Check Jira API rate limits (default: 60 req/min)

### Issue: Charts not rendering

**Solution**:
1. Check browser console for JavaScript errors
2. Verify Chart.js CDN is accessible: `curl https://cdn.jsdelivr.net/npm/chart.js`
3. Ensure `/api/charts/status` and `/api/charts/priority` return valid JSON

### Issue: Database queries slow (>200ms)

**Solution**:
1. Check indexes exist: `\di` in psql
2. Run `ANALYZE issues;` to update query planner statistics
3. Add indexes if missing: `CREATE INDEX idx_issues_status ON issues(status);`

---

## Next Steps

After validating all test scenarios:

1. ✅ Mark feature as "Ready for Production"
2. ✅ Deploy to staging environment
3. ✅ Conduct user acceptance testing (UAT) with 2-3 support team members
4. ✅ Collect feedback and iterate
5. ✅ Deploy to production
6. ✅ Monitor usage analytics and performance metrics
