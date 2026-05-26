/**
 * Unified Dashboard for EEG and Face Emotion Recognition
 * Real-time updates with Chart.js visualizations
 */

class UnifiedEmotionDashboard {
    constructor() {
        // Configuration
        this.updateInterval = 5000; // 5 seconds
        this.maxTimelineItems = 10;
        this.maxChartDataPoints = 20;
        
        // Data storage
        this.eegData = {
            emotion: 'neutral',
            confidence: 0,
            timestamp: null,
            emoji: '😐'
        };
        
        this.faceData = {
            emotion: 'neutral',
            confidence: 0,
            timestamp: null,
            emoji: '😐'
        };
        
        this.emotionHistory = {
            eeg: [],
            face: []
        };
        
        this.emotionCounts = {
            eeg: {},
            face: {}
        };
        
        // Emotion emoji mapping
        this.emotionEmojis = {
            'happy': '😊',
            'sad': '😢',
            'angry': '😠',
            'fear': '😨',
            'neutral': '😐',
            'surprise': '😲',
            'stress': '😰',
            'relaxed': '😌',
            'excited': '🤩',
            'calm': '😌'
        };
        
        // Emotion colors
        this.emotionColors = {
            'happy': '#FFD700',
            'sad': '#4169E1',
            'angry': '#DC143C',
            'fear': '#9370DB',
            'neutral': '#808080',
            'surprise': '#FF69B4',
            'stress': '#FF4500',
            'relaxed': '#32CD32',
            'excited': '#FF1493',
            'calm': '#87CEEB'
        };
        
        // Charts
        this.charts = {};
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('Initializing Unified Emotion Dashboard...');
        
        // Initialize charts
        this.initCharts();
        
        // Load initial data
        this.loadData();
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        console.log('Dashboard initialized successfully');
    }
    
    initCharts() {
        // Emotion Distribution Chart (Pie)
        const distCtx = document.getElementById('emotionDistributionChart');
        if (distCtx) {
            this.charts.distribution = new Chart(distCtx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'EEG',
                        data: [],
                        backgroundColor: []
                    }, {
                        label: 'Face',
                        data: [],
                        backgroundColor: []
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        title: {
                            display: false
                        }
                    }
                }
            });
        }
        
        // Emotion Timeline Chart (Line)
        const timelineCtx = document.getElementById('emotionTimelineChart');
        if (timelineCtx) {
            this.charts.timeline = new Chart(timelineCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'EEG Confidence',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Face Confidence',
                        data: [],
                        borderColor: '#38ef7d',
                        backgroundColor: 'rgba(56, 239, 125, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        // Confidence Comparison Chart (Bar)
        const confCtx = document.getElementById('confidenceComparisonChart');
        if (confCtx) {
            this.charts.confidence = new Chart(confCtx, {
                type: 'bar',
                data: {
                    labels: ['Happy', 'Sad', 'Angry', 'Fear', 'Neutral', 'Surprise', 'Stress', 'Relaxed'],
                    datasets: [{
                        label: 'EEG',
                        data: [0, 0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: '#667eea'
                    }, {
                        label: 'Face',
                        data: [0, 0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: '#38ef7d'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }
    
    async loadData() {
        try {
            // Load EEG data
            await this.loadEEGData();
            
            // Load Face data
            await this.loadFaceData();
            
            // Update displays
            this.updateDisplays();
            
            // Update charts
            this.updateCharts();
            
            // Update statistics
            this.updateStatistics();
            
            // Update last update time
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            
        } catch (error) {
            console.error('Error loading data:', error);
        }
    }
    
    async loadEEGData() {
        try {
            const response = await fetch('/ml/api/latest-prediction/');
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.prediction) {
                    this.eegData = {
                        emotion: data.prediction.predicted_emotion,
                        confidence: data.prediction.confidence_score * 100,
                        timestamp: new Date(data.prediction.prediction_date),
                        emoji: this.emotionEmojis[data.prediction.predicted_emotion] || '😐'
                    };
                    
                    // Add to history
                    this.emotionHistory.eeg.push({
                        emotion: this.eegData.emotion,
                        confidence: this.eegData.confidence,
                        timestamp: this.eegData.timestamp
                    });
                    
                    // Keep only recent items
                    if (this.emotionHistory.eeg.length > this.maxChartDataPoints) {
                        this.emotionHistory.eeg.shift();
                    }
                    
                    // Update counts
                    this.emotionCounts.eeg[this.eegData.emotion] = 
                        (this.emotionCounts.eeg[this.eegData.emotion] || 0) + 1;
                }
            }
        } catch (error) {
            console.error('Error loading EEG data:', error);
        }
    }
    
    async loadFaceData() {
        try {
            const response = await fetch('/face-emotion/api/statistics/');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Get latest prediction (you may need to add an endpoint for this)
                    const historyResponse = await fetch('/face-emotion/api/latest-prediction/');
                    if (historyResponse.ok) {
                        const historyData = await historyResponse.json();
                        if (historyData.success && historyData.prediction) {
                            this.faceData = {
                                emotion: historyData.prediction.predicted_emotion,
                                confidence: historyData.prediction.confidence_score * 100,
                                timestamp: new Date(historyData.prediction.prediction_date),
                                emoji: this.emotionEmojis[historyData.prediction.predicted_emotion] || '😐'
                            };
                            
                            // Add to history
                            this.emotionHistory.face.push({
                                emotion: this.faceData.emotion,
                                confidence: this.faceData.confidence,
                                timestamp: this.faceData.timestamp
                            });
                            
                            // Keep only recent items
                            if (this.emotionHistory.face.length > this.maxChartDataPoints) {
                                this.emotionHistory.face.shift();
                            }
                            
                            // Update counts
                            this.emotionCounts.face[this.faceData.emotion] = 
                                (this.emotionCounts.face[this.faceData.emotion] || 0) + 1;
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error loading Face data:', error);
        }
    }
    
    updateDisplays() {
        // Update EEG display
        document.getElementById('eegEmotionEmoji').textContent = this.eegData.emoji;
        document.getElementById('eegEmotionText').textContent = 
            this.eegData.emotion.charAt(0).toUpperCase() + this.eegData.emotion.slice(1);
        document.getElementById('eegConfidenceFill').style.width = this.eegData.confidence + '%';
        document.getElementById('eegConfidenceText').textContent = 
            this.eegData.confidence.toFixed(1) + '%';
        
        if (this.eegData.timestamp) {
            document.getElementById('eegTimestamp').textContent = 
                this.formatTimestamp(this.eegData.timestamp);
        }
        
        // Update Face display
        document.getElementById('faceEmotionEmoji').textContent = this.faceData.emoji;
        document.getElementById('faceEmotionText').textContent = 
            this.faceData.emotion.charAt(0).toUpperCase() + this.faceData.emotion.slice(1);
        document.getElementById('faceConfidenceFill').style.width = this.faceData.confidence + '%';
        document.getElementById('faceConfidenceText').textContent = 
            this.faceData.confidence.toFixed(1) + '%';
        
        if (this.faceData.timestamp) {
            document.getElementById('faceTimestamp').textContent = 
                this.formatTimestamp(this.faceData.timestamp);
        }
        
        // Update comparison
        this.updateComparison();
        
        // Update activity timeline
        this.updateActivityTimeline();
    }
    
    updateComparison() {
        // Update comparison displays
        document.getElementById('eegComparisonEmoji').textContent = this.eegData.emoji;
        document.getElementById('eegComparisonText').textContent = 
            this.eegData.emotion.charAt(0).toUpperCase() + this.eegData.emotion.slice(1);
        document.getElementById('eegComparisonConf').textContent = 
            this.eegData.confidence.toFixed(1) + '% confidence';
        
        document.getElementById('faceComparisonEmoji').textContent = this.faceData.emoji;
        document.getElementById('faceComparisonText').textContent = 
            this.faceData.emotion.charAt(0).toUpperCase() + this.faceData.emotion.slice(1);
        document.getElementById('faceComparisonConf').textContent = 
            this.faceData.confidence.toFixed(1) + '% confidence';
        
        // Check agreement
        const agreementDiv = document.getElementById('agreementStatus');
        if (this.eegData.emotion === this.faceData.emotion) {
            agreementDiv.className = 'alert alert-success';
            agreementDiv.innerHTML = `
                <i class="fas fa-check-circle"></i> 
                <strong>Agreement!</strong> Both systems detected: ${this.eegData.emotion}
            `;
        } else {
            agreementDiv.className = 'alert alert-warning';
            agreementDiv.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i> 
                <strong>Different Results:</strong> EEG detected ${this.eegData.emotion}, 
                Face detected ${this.faceData.emotion}
            `;
        }
    }
    
    updateActivityTimeline() {
        const timeline = document.getElementById('activityTimeline');
        const activities = [];
        
        // Combine and sort activities
        this.emotionHistory.eeg.forEach(item => {
            activities.push({
                type: 'EEG',
                ...item
            });
        });
        
        this.emotionHistory.face.forEach(item => {
            activities.push({
                type: 'Face',
                ...item
            });
        });
        
        activities.sort((a, b) => b.timestamp - a.timestamp);
        
        // Display recent activities
        if (activities.length === 0) {
            timeline.innerHTML = '<p class="text-muted text-center">No recent activity</p>';
            return;
        }
        
        let html = '';
        activities.slice(0, this.maxTimelineItems).forEach(activity => {
            const emoji = this.emotionEmojis[activity.emotion] || '😐';
            const color = activity.type === 'EEG' ? '#667eea' : '#38ef7d';
            
            html += `
                <div class="timeline-item" style="border-left-color: ${color};">
                    <div class="timeline-time">${this.formatTimestamp(activity.timestamp)}</div>
                    <div class="timeline-content">
                        <strong>${activity.type}</strong>: 
                        ${emoji} ${activity.emotion.charAt(0).toUpperCase() + activity.emotion.slice(1)} 
                        (${activity.confidence.toFixed(1)}%)
                    </div>
                </div>
            `;
        });
        
        timeline.innerHTML = html;
    }
    
    updateCharts() {
        this.updateDistributionChart();
        this.updateTimelineChart();
        this.updateConfidenceChart();
    }
    
    updateDistributionChart() {
        if (!this.charts.distribution) return;
        
        const emotions = Object.keys(this.emotionCounts.eeg).concat(
            Object.keys(this.emotionCounts.face)
        );
        const uniqueEmotions = [...new Set(emotions)];
        
        const eegData = uniqueEmotions.map(e => this.emotionCounts.eeg[e] || 0);
        const faceData = uniqueEmotions.map(e => this.emotionCounts.face[e] || 0);
        const colors = uniqueEmotions.map(e => this.emotionColors[e] || '#808080');
        
        this.charts.distribution.data.labels = uniqueEmotions.map(e => 
            e.charAt(0).toUpperCase() + e.slice(1)
        );
        this.charts.distribution.data.datasets[0].data = eegData;
        this.charts.distribution.data.datasets[0].backgroundColor = colors;
        this.charts.distribution.data.datasets[1].data = faceData;
        this.charts.distribution.data.datasets[1].backgroundColor = colors.map(c => c + '80');
        
        this.charts.distribution.update();
    }
    
    updateTimelineChart() {
        if (!this.charts.timeline) return;
        
        const maxLength = Math.max(
            this.emotionHistory.eeg.length,
            this.emotionHistory.face.length
        );
        
        const labels = Array.from({length: maxLength}, (_, i) => i + 1);
        const eegConfidences = this.emotionHistory.eeg.map(item => item.confidence);
        const faceConfidences = this.emotionHistory.face.map(item => item.confidence);
        
        this.charts.timeline.data.labels = labels;
        this.charts.timeline.data.datasets[0].data = eegConfidences;
        this.charts.timeline.data.datasets[1].data = faceConfidences;
        
        this.charts.timeline.update();
    }
    
    updateConfidenceChart() {
        if (!this.charts.confidence) return;
        
        // Calculate average confidence for each emotion
        const emotions = ['happy', 'sad', 'angry', 'fear', 'neutral', 'surprise', 'stress', 'relaxed'];
        
        const eegAvg = emotions.map(emotion => {
            const items = this.emotionHistory.eeg.filter(item => item.emotion === emotion);
            if (items.length === 0) return 0;
            return items.reduce((sum, item) => sum + item.confidence, 0) / items.length;
        });
        
        const faceAvg = emotions.map(emotion => {
            const items = this.emotionHistory.face.filter(item => item.emotion === emotion);
            if (items.length === 0) return 0;
            return items.reduce((sum, item) => sum + item.confidence, 0) / items.length;
        });
        
        this.charts.confidence.data.datasets[0].data = eegAvg;
        this.charts.confidence.data.datasets[1].data = faceAvg;
        
        this.charts.confidence.update();
    }
    
    updateStatistics() {
        const totalEEG = this.emotionHistory.eeg.length;
        const totalFace = this.emotionHistory.face.length;
        const total = totalEEG + totalFace;
        
        document.getElementById('totalPredictions').textContent = total;
        document.getElementById('eegPredictions').textContent = totalEEG;
        document.getElementById('facePredictions').textContent = totalFace;
        
        // Calculate average confidence
        const allConfidences = [
            ...this.emotionHistory.eeg.map(item => item.confidence),
            ...this.emotionHistory.face.map(item => item.confidence)
        ];
        
        const avgConf = allConfidences.length > 0
            ? allConfidences.reduce((sum, conf) => sum + conf, 0) / allConfidences.length
            : 0;
        
        document.getElementById('avgConfidence').textContent = avgConf.toFixed(1) + '%';
    }
    
    formatTimestamp(timestamp) {
        const now = new Date();
        const diff = now - timestamp;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            const minutes = Math.floor(diff / 60000);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else if (diff < 86400000) { // Less than 1 day
            const hours = Math.floor(diff / 3600000);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            return timestamp.toLocaleString();
        }
    }
    
    startAutoRefresh() {
        setInterval(() => {
            this.loadData();
        }, this.updateInterval);
        
        console.log(`Auto-refresh enabled (every ${this.updateInterval/1000} seconds)`);
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.unifiedDashboard = new UnifiedEmotionDashboard();
    console.log('Unified Emotion Dashboard loaded');
});

// Made with Bob
