/**
 * Filters and search functionality for issue table
 *
 * Handles:
 * - Text search in jira_key and summary
 * - Priority filter
 * - Pagination controls
 * - Dynamic table rendering
 */

// Current filter state
let currentFilters = {
    search: '',
    priority: '',
    page: 1,
    per_page: 10
};

/**
 * Fetch and render issues based on current filters
 */
async function loadIssues() {
    try {
        // Build query string
        const params = new URLSearchParams();
        if (currentFilters.search) params.append('search', currentFilters.search);
        if (currentFilters.priority) params.append('priority', currentFilters.priority);
        params.append('page', currentFilters.page);
        params.append('per_page', currentFilters.per_page);

        // Fetch issues from API
        const response = await fetch(`/api/issues?${params.toString()}`);
        const data = await response.json();

        // Render table
        renderTable(data.issues);

        // Update pagination controls
        updatePaginationControls(data.pagination);
    } catch (error) {
        console.error('Error loading issues:', error);
        renderError();
    }
}

/**
 * Render issue table with data
 */
function renderTable(issues) {
    const tbody = document.getElementById('issue-table-body');

    if (!tbody) {
        console.error('Table body not found');
        return;
    }

    if (issues.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="no-results">No issues found</td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = issues.map(issue => `
        <tr>
            <td class="issue-key">${escapeHtml(issue.jira_key)}</td>
            <td class="issue-summary">${escapeHtml(issue.summary)}</td>
            <td class="issue-assignee">
                ${issue.assignee_name ?
                    escapeHtml(issue.assignee_name) :
                    '<span class="unassigned">Unassigned</span>'}
            </td>
            <td class="issue-priority priority-${issue.priority.toLowerCase().replace(' ', '-')}">
                ${escapeHtml(issue.priority)}
            </td>
            <td class="issue-status status-${issue.status.toLowerCase().replace(' ', '-')}">
                ${escapeHtml(issue.status)}
            </td>
        </tr>
    `).join('');
}

/**
 * Update pagination controls
 */
function updatePaginationControls(pagination) {
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');

    if (!prevBtn || !nextBtn || !pageInfo) {
        return;
    }

    // Update button states
    prevBtn.disabled = !pagination.has_prev;
    nextBtn.disabled = !pagination.has_next;

    // Update page info
    pageInfo.textContent = pagination.total_pages > 0 ?
        `Page ${pagination.page} of ${pagination.total_pages}` :
        'No pages';
}

/**
 * Render error message
 */
function renderError() {
    const tbody = document.getElementById('issue-table-body');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="error-message">
                    Error loading issues. Please try again.
                </td>
            </tr>
        `;
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Handle search input change with debouncing
 */
let searchTimeout;
function handleSearchInput(event) {
    const searchText = event.target.value.trim();

    // Debounce search (wait 300ms after user stops typing)
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        currentFilters.search = searchText;
        currentFilters.page = 1; // Reset to first page
        loadIssues();
    }, 300);
}

/**
 * Handle priority filter change
 */
function handlePriorityChange(event) {
    currentFilters.priority = event.target.value;
    currentFilters.page = 1; // Reset to first page
    loadIssues();
}

/**
 * Handle previous page button click
 */
function handlePreviousPage() {
    if (currentFilters.page > 1) {
        currentFilters.page--;
        loadIssues();
    }
}

/**
 * Handle next page button click
 */
function handleNextPage() {
    currentFilters.page++;
    loadIssues();
}

/**
 * Initialize event listeners when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Search input
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearchInput);
    }

    // Priority filter
    const priorityFilter = document.getElementById('priority-filter');
    if (priorityFilter) {
        priorityFilter.addEventListener('change', handlePriorityChange);
    }

    // Pagination buttons
    const prevBtn = document.getElementById('prev-page');
    if (prevBtn) {
        prevBtn.addEventListener('click', handlePreviousPage);
    }

    const nextBtn = document.getElementById('next-page');
    if (nextBtn) {
        nextBtn.addEventListener('click', handleNextPage);
    }

    // Load initial data
    loadIssues();
});
