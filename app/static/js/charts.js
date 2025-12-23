/**
 * Charts initialization for Support Team Dashboard
 *
 * Fetches data from API endpoints and renders:
 * - Bar chart for status distribution
 * - Pie chart for priority distribution
 */

// Dark theme colors for Chart.js
const CHART_COLORS = {
    primary: '#4a9eff',
    critical: '#ff4444',
    high: '#ff9944',
    medium: '#ffdd44',
    low: '#44ff44',
    toDo: '#4a9eff',
    inProgress: '#ff9944',
    done: '#44ff88',
    background: '#2d2d2d',
    text: '#e0e0e0',
    border: '#404040'
};

// Chart.js default configuration for dark theme
Chart.defaults.color = CHART_COLORS.text;
Chart.defaults.borderColor = CHART_COLORS.border;
Chart.defaults.backgroundColor = CHART_COLORS.background;

/**
 * Fetch and render status distribution bar chart
 */
async function renderStatusChart() {
    try {
        const response = await fetch('/api/charts/status');
        const data = await response.json();

        const ctx = document.getElementById('status-chart');
        if (!ctx) {
            console.error('Status chart canvas not found');
            return;
        }

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Issues by Status',
                    data: data.data,
                    backgroundColor: [
                        CHART_COLORS.toDo,
                        CHART_COLORS.inProgress,
                        CHART_COLORS.done
                    ],
                    borderColor: [
                        CHART_COLORS.toDo,
                        CHART_COLORS.inProgress,
                        CHART_COLORS.done
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        grid: {
                            color: CHART_COLORS.border
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading status chart:', error);
    }
}

/**
 * Fetch and render priority distribution pie chart
 */
async function renderPriorityChart() {
    try {
        const response = await fetch('/api/charts/priority');
        const data = await response.json();

        const ctx = document.getElementById('priority-chart');
        if (!ctx) {
            console.error('Priority chart canvas not found');
            return;
        }

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Open Issues by Priority',
                    data: data.data,
                    backgroundColor: [
                        CHART_COLORS.critical,
                        CHART_COLORS.high,
                        CHART_COLORS.medium,
                        CHART_COLORS.low
                    ],
                    borderColor: CHART_COLORS.background,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: CHART_COLORS.text,
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    title: {
                        display: false
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading priority chart:', error);
    }
}

/**
 * Initialize all charts when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    renderStatusChart();
    renderPriorityChart();
});
