/**
 * Dashboard functionality for Inventory AI
 * Handles data loading and display for dashboard widgets
 */

class DashboardManager {
    constructor() {
        this.apiKey = window.API_KEY;
        this.initializeDashboard();
    }
    
    async initializeDashboard() {
        try {
            await this.loadDashboardData();
            this.setupAutoRefresh();
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.showError('Failed to initialize dashboard');
        }
    }
    
    async loadDashboardData() {
        try {
            // Load today's orders
            await this.loadTodayOrders();
            
            // Load today's snapshots
            await this.loadTodaySnapshots();
            
            // Load today's anomalies
            await this.loadTodayAnomalies();
            
            // Load bins scanned
            await this.loadBinsScanned();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }
    
    async loadTodayOrders() {
        try {
            const response = await fetch('/api/orders/today', {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                document.getElementById('today-orders').textContent = data.count || 0;
            } else {
                document.getElementById('today-orders').textContent = '0';
            }
        } catch (error) {
            console.error('Error loading today orders:', error);
            document.getElementById('today-orders').textContent = '0';
        }
    }
    
    async loadTodaySnapshots() {
        try {
            const response = await fetch('/api/snapshots/today', {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                document.getElementById('today-snapshots').textContent = data.count || 0;
            } else {
                document.getElementById('today-snapshots').textContent = '0';
            }
        } catch (error) {
            console.error('Error loading today snapshots:', error);
            document.getElementById('today-snapshots').textContent = '0';
        }
    }
    
    async loadTodayAnomalies() {
        try {
            const response = await fetch('/api/reconcile/anomalies/today', {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                document.getElementById('today-anomalies').textContent = data.count || 0;
            } else {
                document.getElementById('today-anomalies').textContent = '0';
            }
        } catch (error) {
            console.error('Error loading today anomalies:', error);
            document.getElementById('today-anomalies').textContent = '0';
        }
    }
    
    async loadBinsScanned() {
        try {
            const response = await fetch('/api/snapshots/bins/today', {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                document.getElementById('bins-scanned').textContent = data.count || 0;
            } else {
                document.getElementById('bins-scanned').textContent = '0';
            }
        } catch (error) {
            console.error('Error loading bins scanned:', error);
            document.getElementById('bins-scanned').textContent = '0';
        }
    }
    
    setupAutoRefresh() {
        // Refresh dashboard data every 5 minutes
        setInterval(() => {
            this.loadDashboardData();
        }, 5 * 60 * 1000);
    }
    
    showError(message) {
        console.error(message);
        // You can implement a notification system here
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('today-orders')) {
        window.dashboardManager = new DashboardManager();
    }
});

// Global function for reconciliation
async function runReconciliation() {
    try {
        const apiKey = window.API_KEY;
        const response = await fetch('/api/reconcile/run', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: new Date().toISOString().split('T')[0]
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(`Reconciliation started! Job ID: ${data.job_id}`);
        } else {
            const error = await response.json();
            alert(`Reconciliation failed: ${error.detail}`);
        }
    } catch (error) {
        console.error('Reconciliation error:', error);
        alert('Failed to start reconciliation');
    }
}
