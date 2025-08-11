// Dashboard Configuration
const DashboardConfig = {
    colors: {
        primary: '#007bff',
        success: '#28a745',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#17a2b8'
    },
    
    // Fallback data for when backend data is unavailable
    fallbackData: {
        payment_stats: {
            monthly_revenue: [
                { month_name: "Jan", revenue: 5000000 },
                { month_name: "Feb", revenue: 7000000 },
                { month_name: "Mar", revenue: 8500000 },
                { month_name: "Apr", revenue: 4800000 },
                { month_name: "May", revenue: 9200000 },
                { month_name: "Jun", revenue: 6500000 }
            ]
        },
        room_stats: { occupied_rooms: 12, available_rooms: 38, maintenance_rooms: 2 },
        contract_stats: { active_contracts: 15, expiring_soon: 3, expired_contracts: 1 },
        user_stats: { total_students: 45, total_staff: 8, total_admins: 3 }
    }
};

// Dashboard Data Management
class DashboardManager {
    constructor(backendData) {
        this.data = this.initializeData(backendData);
    }
    
    initializeData(backendData) {
        return Object.keys(backendData).length > 0 ? { stats: backendData } : { stats: DashboardConfig.fallbackData };
    }
    
    formatCurrency(value) {
        return new Intl.NumberFormat('vi-VN').format(value) + 'đ';
    }
}

// Chart Management
class ChartManager {
    constructor(dashboardManager) {
        this.dashboard = dashboardManager;
    }
    
    createRevenueChart() {
        const ctx = document.getElementById('revenueChart');
        const monthlyData = this.dashboard.data.stats.payment_stats?.monthly_revenue || [];
        
        if (!ctx || !monthlyData.length) return;
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: monthlyData.map(item => item.month_name),
                datasets: [{
                    label: 'Doanh thu (VND)',
                    data: monthlyData.map(item => item.revenue),
                    borderColor: DashboardConfig.colors.primary,
                    backgroundColor: DashboardConfig.colors.primary + '20',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: (value) => this.dashboard.formatCurrency(value) }
                    }
                }
            }
        });
    }
    
    createRoomStatusChart() {
        const ctx = document.getElementById('roomStatusChart');
        const roomStats = this.dashboard.data.stats.room_stats;
        
        if (!ctx || !roomStats) return;
        
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Phòng đã thuê', 'Phòng trống', 'Bảo trì'],
                datasets: [{
                    data: [
                        roomStats.occupied_rooms || 0,
                        roomStats.available_rooms || 0,
                        roomStats.maintenance_rooms || 0
                    ],
                    backgroundColor: [
                        DashboardConfig.colors.success,
                        DashboardConfig.colors.warning,
                        DashboardConfig.colors.danger
                    ],
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 20, usePointStyle: true }
                    }
                }
            }
        });
    }
    
    createContractChart() {
        const ctx = document.getElementById('contractChart');
        const contractStats = this.dashboard.data.stats.contract_stats;
        
        if (!ctx || !contractStats) return;
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Hiệu lực', 'Sắp hết hạn', 'Đã hết hạn'],
                datasets: [{
                    label: 'Số lượng',
                    data: [
                        contractStats.active_contracts || 0,
                        contractStats.expiring_soon || 0,
                        contractStats.expired_contracts || 0
                    ],
                    backgroundColor: [
                        DashboardConfig.colors.success,
                        DashboardConfig.colors.warning,
                        DashboardConfig.colors.danger
                    ],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                }
            }
        });
    }
    
    createUserChart() {
        const ctx = document.getElementById('userChart');
        const userStats = this.dashboard.data.stats.user_stats;
        
        if (!ctx || !userStats) return;
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Sinh viên', 'Nhân viên', 'Quản trị viên'],
                datasets: [{
                    data: [
                        userStats.total_students || 0,
                        userStats.total_staff || 0,
                        userStats.total_admins || 0
                    ],
                    backgroundColor: [
                        DashboardConfig.colors.info,
                        DashboardConfig.colors.primary,
                        DashboardConfig.colors.warning
                    ],
                    borderWidth: 3,
                    borderColor: '#fff',
                    cutout: '60%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 20, usePointStyle: true }
                    }
                }
            }
        });
    }
    
    initializeAllCharts() {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not loaded');
            return;
        }
        
        this.createRevenueChart();
        this.createRoomStatusChart();
        this.createContractChart();
        this.createUserChart();
    }
}

// Activity Management
function refreshActivities() {
    const activitiesList = document.getElementById('activitiesList');
    const activitiesLoading = document.getElementById('activitiesLoading');
    
    if (!activitiesList || !activitiesLoading) return;
    
    activitiesLoading.style.display = 'block';
    activitiesList.style.opacity = '0.5';
    
    // Get the activities URL from the global variable set in the template
    const activitiesUrl = window.dashboardUrls?.recent_activities;
    if (!activitiesUrl) {
        console.error('Activities URL not found');
        return;
    }
    
    fetch(activitiesUrl)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.activities) {
                updateActivitiesList(data.activities);
            }
        })
        .catch(error => console.error('Error fetching activities:', error))
        .finally(() => {
            activitiesLoading.style.display = 'none';
            activitiesList.style.opacity = '1';
        });
}

function updateActivitiesList(activities) {
    const activitiesList = document.getElementById('activitiesList');
    
    if (!activities?.length) {
        activitiesList.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-info-circle fa-2x text-muted mb-2"></i>
                <p class="text-muted">Chưa có hoạt động gần đây</p>
            </div>
        `;
        return;
    }
    
    activitiesList.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <i class="${activity.icon} text-${activity.color}"></i>
                    <span class="ms-2">${activity.message}</span>
                    ${activity.status ? `<span class="badge bg-${activity.color} ms-2">${activity.status}</span>` : ''}
                </div>
                <small class="text-muted">${activity.relative_time}</small>
            </div>
        </div>
    `).join('');
}

// Initialize Dashboard
function initializeDashboard(backendData) {
    // Hide loading spinner
    const mainLoading = document.getElementById('mainLoading');
    if (mainLoading) mainLoading.style.display = 'none';
    
    // Initialize dashboard components
    const dashboardManager = new DashboardManager(backendData || {});
    const chartManager = new ChartManager(dashboardManager);
    
    // Create all charts
    chartManager.initializeAllCharts();
    
    // Setup clickable alerts
    document.querySelectorAll('.alert-item[onclick]').forEach(item => {
        item.style.cursor = 'pointer';
    });
    
    // Auto-refresh activities every 5 minutes
    setInterval(refreshActivities, 5 * 60 * 1000);
}

// Export for module usage (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DashboardConfig,
        DashboardManager,
        ChartManager,
        refreshActivities,
        initializeDashboard
    };
}
