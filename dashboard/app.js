// Chart Default Styling for Dark Theme
Chart.defaults.color = '#8ea4b8';
Chart.defaults.font.family = "'Outfit', sans-serif";
Chart.defaults.scale.grid.color = 'rgba(255, 255, 255, 0.05)';

// Configuration Paths
const DATA_PATHS = {
    capacity: '../outputs/powerbi_ready/capacity_report.csv',
    forecast: '../outputs/powerbi_ready/forecast_report.csv',
    alerts: '../outputs/powerbi_ready/alerts_report.csv',
    productivity: '../outputs/powerbi_ready/productivity_report.csv',
    scenarios: '../outputs/powerbi_ready/scenario_report.csv'
};

// Main Initialization
document.addEventListener('DOMContentLoaded', () => {
    loadCapacityKPIs();
    loadForecastChart();
    loadAlertsFeed();
    loadProductivityChart();
    loadScenarioMatrix();
});

// Helper for PapaParse Native Fetching
function fetchCSV(url, callback) {
    Papa.parse(url, {
        download: true,
        header: true,
        dynamicTyping: true,
        complete: function(results) {
            callback(results.data.filter(row => Object.keys(row).length > 1)); // filter empties
        },
        error: function(err) {
            console.error("Dashboard Load Error:", err);
        }
    });
}

// 1. Load Top KPIs
function loadCapacityKPIs() {
    fetchCSV(DATA_PATHS.capacity, (data) => {
        let maxCap = 0;
        let seen = 0;
        data.forEach(row => {
            if (row.Metric === 'Maximum_System_Capacity') maxCap = row.Value;
            if (row.Metric === 'Total_Patients_Seen') seen = row.Value;
        });
        
        let util = 0;
        if(maxCap > 0) util = (seen / maxCap) * 100;
        
        const el = document.getElementById('kpi-capacity');
        
        // Counter Animation
        animateValue(el, 0, util, 1500, (val) => val.toFixed(1) + "%");
    });
}

// 2. ARIMAX Forecast Chart (Line)
function loadForecastChart() {
    fetchCSV(DATA_PATHS.forecast, (data) => {
        if(!data || data.length === 0) return;
        
        const labels = data.map(row => row.Forecast_Month);
        const revenue = data.map(row => row.Projected_Revenue);
        const upper = data.map(row => row['Revenue_Upper_Bound (95%)']);
        const lower = data.map(row => row['Revenue_Lower_Bound (95%)']);
        
        // Set up the next 6-months revenue KPI dynamically
        let sum6Mo = revenue.reduce((a, b) => a + b, 0);
        animateValue(document.getElementById('kpi-revenue'), 0, sum6Mo, 2000, (val) => "$" + (val/1000000).toFixed(2) + "M");

        const ctx = document.getElementById('forecastChart').getContext('2d');
        
        // Gradient Fill
        let gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(0, 242, 254, 0.4)');
        gradient.addColorStop(1, 'rgba(0, 242, 254, 0.05)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Projected Revenue ($)',
                        data: revenue,
                        borderColor: '#00f2fe',
                        backgroundColor: gradient,
                        borderWidth: 3,
                        pointBackgroundColor: '#fff',
                        pointBorderColor: '#00f2fe',
                        pointRadius: 4,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Upper 95% CI',
                        data: upper,
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0,
                        tension: 0.4
                    },
                    {
                        label: 'Lower 95% CI',
                        data: lower,
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(20,28,43,0.9)',
                        titleColor: '#fff',
                        bodyColor: '#00f2fe',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderWidth: 1
                    }
                },
                interaction: { mode: 'nearest', axis: 'x', intersect: false },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) { return '$' + value / 1000 + 'k'; }
                        }
                    }
                }
            }
        });
    });
}

// 3. Command Center Alerts
function loadAlertsFeed() {
    fetchCSV(DATA_PATHS.alerts, (data) => {
        const list = document.getElementById('alertsList');
        list.innerHTML = '';
        
        let redCount = 0;
        
        if(!data || data.length === 0) {
            list.innerHTML = `<li><span class="alert-title">System Normal</span><span class="alert-impact">Zero automated triggers detected in the current governance sweep.</span></li>`;
            document.getElementById('kpi-alerts').innerText = "0 Threats";
            return;
        }

        data.forEach(row => {
            const li = document.createElement('li');
            li.className = row.Severity === 'RED FLAG' ? 'alert-red' : 'alert-yellow';
            if(row.Severity === 'RED FLAG') redCount++;
            
            li.innerHTML = `
                <span class="alert-title">[${row.Alert_Type}] ${row.Entity}</span>
                <span style="color:#eee; font-size:0.85rem">${row.Trigger}</span>
                <span class="alert-impact">${row.Impact}</span>
            `;
            list.appendChild(li);
        });
        
        document.getElementById('kpi-alerts').innerText = `${redCount} Critical`;
    });
}

// 4. Productivity Profile (Bar Chart)
function loadProductivityChart() {
    fetchCSV(DATA_PATHS.productivity, (data) => {
        if(!data || data.length === 0) return;
        
        // Isolate top 15 for readability
        let cohort = data.filter(r => r.State === 'MD' || r.State === 'NY').slice(0, 15);
        if(cohort.length === 0) cohort = data.slice(0, 15);
        
        cohort.sort((a,b) => b.Total_RVUs_Annual - a.Total_RVUs_Annual);
        
        const labels = cohort.map(r => r.Physician_Name.split(' ')[0] + " " + r.Physician_Name.split(' ').pop());
        const rvus = cohort.map(r => r.Total_RVUs_Annual);
        
        const ctx = document.getElementById('productivityChart').getContext('2d');
        
        let gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, '#4facfe');
        gradient.addColorStop(1, '#00f2fe');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Annual RVU Generation',
                    data: rvus,
                    backgroundColor: gradient,
                    borderRadius: 4,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(20,28,43,0.9)',
                        bodyColor: '#4facfe'
                    }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    });
}

// 5. Scenario Modeler Matrix
function loadScenarioMatrix() {
    fetchCSV(DATA_PATHS.scenarios, (data) => {
        const grid = document.getElementById('scenarioMatrix');
        grid.innerHTML = '';
        
        if(!data || data.length === 0) return;
        
        data.forEach(row => {
            const impact = row.Revenue_Impact_Delta;
            let valClass = 'neutral-val';
            let prefix = '';
            
            if(impact > 0) { valClass = 'positive-val'; prefix = '+'; }
            else if(impact < 0) { valClass = 'negative-val'; }
            
            let formattedImpact = prefix + "$" + (Math.abs(impact) / 1000).toFixed(0) + "k";
            if(impact === 0) formattedImpact = "Baseline";
            
            const div = document.createElement('div');
            div.className = 'matrix-row';
            div.innerHTML = `
                <div class="matrix-label">${row.Parameter_Change}</div>
                <div class="matrix-value ${valClass}">${formattedImpact}</div>
            `;
            grid.appendChild(div);
        });
    });
}

// Utility Function for Number Counters
function animateValue(obj, start, end, duration, formatter) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        // easeOutQuart curve
        const ease = 1 - Math.pow(1 - progress, 4);
        const current = Math.floor(start + ease * (end - start));
        obj.innerHTML = formatter ? formatter(current) : current;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.innerHTML = formatter ? formatter(end) : end;
        }
    };
    window.requestAnimationFrame(step);
}
