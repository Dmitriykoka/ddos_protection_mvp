document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const startNormalBtn = document.getElementById('start-normal');
    const startAttackBtn = document.getElementById('start-attack');
    const stopBtn = document.getElementById('stop-traffic');
    const blockIpBtn = document.getElementById('block-ip');
    const alertBox = document.getElementById('alert-box');
    const detectionStatus = document.getElementById('detection-status');
    const blockedIpsCount = document.getElementById('blocked-ips');
    const normalCount = document.getElementById('normal-count');
    const attackCount = document.getElementById('attack-count');
    const normalBar = document.getElementById('normal-bar');
    const attackBar = document.getElementById('attack-bar');

    // Chart initialization
    const ctx = document.getElementById('traffic-chart').getContext('2d');
    const trafficChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array(20).fill(''),
            datasets: [
                {
                    label: 'Normal Traffic',
                    data: Array(20).fill(0),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.1
                },
                {
                    label: 'Attack Traffic',
                    data: Array(20).fill(0),
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Packets/sec'
                    }
                }
            }
        }
    });

    // Update data every second
    setInterval(updateDashboard, 1000);

    // Event listeners
    startNormalBtn.addEventListener('click', () => sendTrafficCommand('start', 'normal'));
    startAttackBtn.addEventListener('click', () => sendTrafficCommand('start', 'attack'));
    stopBtn.addEventListener('click', () => sendTrafficCommand('stop'));
    blockIpBtn.addEventListener('click', blockIp);

    async function updateDashboard() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            // Update status
            detectionStatus.textContent = data.detection.is_attack ? 'ATTACK DETECTED' : 'NORMAL';
            detectionStatus.className = data.detection.is_attack ? 'alert alert-danger' : 'alert alert-success';
            blockedIpsCount.textContent = data.detection.blocked_ips_count;
            
            // Update traffic bars
            normalCount.textContent = data.generator.normal;
            attackCount.textContent = data.generator.attack;
            normalBar.style.width = `${Math.min(data.generator.normal / 100, 100)}%`;
            attackBar.style.width = `${Math.min(data.generator.attack / 1000, 100)}%`;
            
            // Update chart
            updateChart(data);
        } catch (error) {
            console.error('Dashboard update error:', error);
        }
    }

    function updateChart(data) {
        // Shift old data and add new
        trafficChart.data.datasets[0].data.shift();
        trafficChart.data.datasets[1].data.shift();
        trafficChart.data.datasets[0].data.push(data.generator.normal);
        trafficChart.data.datasets[1].data.push(data.generator.attack);
        trafficChart.update();
    }

    async function sendTrafficCommand(action, mode = null) {
        const url = `/api/traffic/${action}${mode ? `?mode=${mode}` : ''}`;
        try {
            const response = await fetch(url, { method: 'POST' });
            const result = await response.json();
            showAlert(result.status === 'started' ? 
                `${mode} traffic started` : 'Traffic stopped', 'success');
        } catch (error) {
            showAlert('Command failed', 'danger');
            console.error('Traffic control error:', error);
        }
    }

    async function blockIp() {
        const ip = prompt('Enter IP to block:');
        if (ip) {
            try {
                await fetch('/api/block', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip })
                });
                showAlert(`IP ${ip} blocked`, 'success');
            } catch (error) {
                showAlert('Block failed', 'danger');
                console.error('Block error:', error);
            }
        }
    }

    function showAlert(message, type) {
        alertBox.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        setTimeout(() => alertBox.innerHTML = '', 3000);
    }
});