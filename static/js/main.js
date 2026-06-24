// MRLMS Global Interactive Controls & Dashboard Analytics

document.addEventListener('DOMContentLoaded', function () {
    // --------------------------------------------------------
    // 1. Sidebar & Mobile Navigation Toggle
    // --------------------------------------------------------
    const sidebar = document.getElementById('sidebar');
    const mainWrapper = document.getElementById('main-wrapper');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (sidebarToggle && sidebar && mainWrapper) {
        sidebarToggle.addEventListener('click', function () {
            if (window.innerWidth >= 992) {
                sidebar.classList.toggle('collapsed');
                mainWrapper.classList.toggle('full-width');
            } else {
                sidebar.classList.toggle('mobile-open');
            }
        });
    }

    // Close mobile sidebar on click outside
    document.addEventListener('click', function (event) {
        if (window.innerWidth < 992 && sidebar && sidebarToggle) {
            if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
                sidebar.classList.remove('mobile-open');
            }
        }
    });

    // --------------------------------------------------------
    // 2. Dark/Light Theme Switching
    // --------------------------------------------------------
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = themeToggleBtn ? themeToggleBtn.querySelector('i') : null;

    // Check saved theme or system default
    const savedTheme = localStorage.getItem('mrlms-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function () {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('mrlms-theme', newTheme);
            updateThemeIcon(newTheme);

            // Re-render charts if they exist to adjust font colors
            if (window.renderDashboardCharts) {
                window.renderDashboardCharts();
            }
        });
    }

    function updateThemeIcon(theme) {
        if (!themeIcon) return;
        if (theme === 'dark') {
            themeIcon.className = 'bi bi-sun-fill';
        } else {
            themeIcon.className = 'bi bi-moon-fill';
        }
    }

    // --------------------------------------------------------
    // 3. Chart.js Dashboard Charts Implementation
    // --------------------------------------------------------
    const analyticsContainer = document.getElementById('analyticsDashboard');
    if (analyticsContainer) {
        // We are on the admin dashboard with analytics panel, load charts
        initAnalytics();
    }
});

let activeCharts = {}; // Save chart instances for redraws

function initAnalytics() {
    fetch('/admin/api/analytics')
        .then(response => {
            if (!response.ok) throw new Error("Failed to load analytics data");
            return response.json();
        })
        .then(data => {
            window.analyticsData = data; // Keep global copy
            window.renderDashboardCharts = function() {
                // Get theme details for chart styling
                const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
                const textMuted = isDark ? '#9ca3af' : '#475569';
                const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.05)';

                const commonOptions = {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: textMuted, font: { family: 'Inter', size: 11 } }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: gridColor },
                            ticks: { color: textMuted, font: { family: 'Inter' } }
                        },
                        y: {
                            grid: { color: gridColor },
                            ticks: { color: textMuted, font: { family: 'Inter' } }
                        }
                    }
                };

                const radialOptions = {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: textMuted, font: { family: 'Inter', size: 11 } }
                        }
                    }
                };

                // Helper to destroy previous chart before draw
                function drawChart(canvasId, config) {
                    if (activeCharts[canvasId]) {
                        activeCharts[canvasId].destroy();
                    }
                    const ctx = document.getElementById(canvasId).getContext('2d');
                    activeCharts[canvasId] = new Chart(ctx, config);
                }

                // Chart 1: Student Enrollment Trends (Bar)
                drawChart('chartEnrollment', {
                    type: 'bar',
                    data: {
                        labels: data.enrollments.labels,
                        datasets: [{
                            label: 'Students Enrolled',
                            data: data.enrollments.data,
                            backgroundColor: '#6366f1',
                            borderRadius: 6
                        }]
                    },
                    options: commonOptions
                });

                // Chart 2: Attendance Trends (Line)
                drawChart('chartAttendance', {
                    type: 'line',
                    data: {
                        labels: data.attendance.labels,
                        datasets: [{
                            label: 'Average Attendance (%)',
                            data: data.attendance.data,
                            borderColor: '#06b6d4',
                            backgroundColor: 'rgba(6, 182, 212, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        ...commonOptions,
                        scales: {
                            ...commonOptions.scales,
                            y: {
                                ...commonOptions.scales.y,
                                min: 0,
                                max: 100
                            }
                        }
                    }
                });

                // Chart 3: Assignment Submission Rates (Doughnut)
                drawChart('chartAssignment', {
                    type: 'doughnut',
                    data: {
                        labels: data.assignments.labels,
                        datasets: [{
                            data: data.assignments.data,
                            backgroundColor: ['#6366f1', '#06b6d4', '#f59e0b', '#10b981', '#ec4899'],
                            borderWidth: 0
                        }]
                    },
                    options: radialOptions
                });

                // Chart 4: Quiz Performance Analysis (Polar Area)
                drawChart('chartQuiz', {
                    type: 'polarArea',
                    data: {
                        labels: data.quizzes.labels,
                        datasets: [{
                            data: data.quizzes.data,
                            backgroundColor: [
                                'rgba(99, 102, 241, 0.6)',
                                'rgba(6, 182, 212, 0.6)',
                                'rgba(245, 158, 11, 0.6)'
                            ],
                            borderColor: isDark ? '#0b0f19' : '#ffffff',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        ...radialOptions,
                        scales: {
                            r: {
                                grid: { color: gridColor },
                                ticks: { backdropColor: 'transparent', color: textMuted }
                            }
                        }
                    }
                });

                // Chart 5: Course Popularity Analysis (Horizontal Bar)
                drawChart('chartPopularity', {
                    type: 'bar',
                    data: {
                        labels: data.popularity.labels,
                        datasets: [{
                            label: 'Enrolled Students',
                            data: data.popularity.data,
                            backgroundColor: '#06b6d4',
                            borderRadius: 6
                        }]
                    },
                    options: {
                        ...commonOptions,
                        indexAxis: 'y'
                    }
                });

                // Chart 6: Student Performance Analysis (Pie)
                drawChart('chartPerformance', {
                    type: 'pie',
                    data: {
                        labels: data.performance.labels,
                        datasets: [{
                            data: data.performance.data,
                            backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
                            borderWidth: 0
                        }]
                    },
                    options: radialOptions
                });

                // Chart 7: Department-wise Analytics (Doughnut)
                drawChart('chartDepartment', {
                    type: 'doughnut',
                    data: {
                        labels: data.departments.labels,
                        datasets: [{
                            data: data.departments.data,
                            backgroundColor: ['#3b82f6', '#10b981', '#8b5cf6', '#ec4899'],
                            borderWidth: 0
                        }]
                    },
                    options: radialOptions
                });

                // Chart 8: Faculty Performance Analytics (Bar)
                drawChart('chartFaculty', {
                    type: 'bar',
                    data: {
                        labels: data.faculty.labels,
                        datasets: [{
                            label: 'Assigned Courses',
                            data: data.faculty.data,
                            backgroundColor: '#8b5cf6',
                            borderRadius: 6
                        }]
                    },
                    options: commonOptions
                });
            };

            window.renderDashboardCharts();
        })
        .catch(err => {
            console.error("Dashboard Analytics Error:", err);
        });
}
