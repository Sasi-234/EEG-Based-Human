/**
 * Webcam Access and Face Emotion Detection
 * Handles WebRTC camera access, frame capture, and emotion prediction
 */

class WebcamEmotionDetector {
    constructor(options = {}) {
        // Configuration
        this.videoElement = options.videoElement || document.getElementById('webcamVideo');
        this.canvasElement = options.canvasElement || document.getElementById('captureCanvas');
        this.resultContainer = options.resultContainer || document.getElementById('emotionResult');
        this.apiEndpoint = options.apiEndpoint || '/face-emotion/api/predict-webcam/';
        this.captureInterval = options.captureInterval || 2000; // ms between captures
        this.autoCapture = options.autoCapture || false;
        
        // State
        this.stream = null;
        this.isCapturing = false;
        this.captureTimer = null;
        this.sessionId = null;
        this.predictionCount = 0;
        this.emotionHistory = [];
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('Initializing Webcam Emotion Detector...');
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Start webcam button
        const startBtn = document.getElementById('startWebcam');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startWebcam());
        }
        
        // Stop webcam button
        const stopBtn = document.getElementById('stopWebcam');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopWebcam());
        }
        
        // Capture button
        const captureBtn = document.getElementById('captureBtn');
        if (captureBtn) {
            captureBtn.addEventListener('click', () => this.captureAndPredict());
        }
        
        // Auto-capture toggle
        const autoToggle = document.getElementById('autoCapture');
        if (autoToggle) {
            autoToggle.addEventListener('change', (e) => {
                this.autoCapture = e.target.checked;
                if (this.autoCapture && this.stream) {
                    this.startAutoCapture();
                } else {
                    this.stopAutoCapture();
                }
            });
        }
    }
    
    async startWebcam() {
        try {
            console.log('Requesting webcam access...');
            
            // Request camera access
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                },
                audio: false
            });
            
            // Set video source
            this.videoElement.srcObject = this.stream;
            
            // Wait for video to load
            await new Promise((resolve) => {
                this.videoElement.onloadedmetadata = () => {
                    this.videoElement.play();
                    resolve();
                };
            });
            
            console.log('Webcam started successfully');
            this.updateUI('started');
            
            // Start session
            await this.startSession();
            
            // Start auto-capture if enabled
            if (this.autoCapture) {
                this.startAutoCapture();
            }
            
            this.showNotification('Webcam started successfully!', 'success');
            
        } catch (error) {
            console.error('Error accessing webcam:', error);
            this.showNotification('Failed to access webcam: ' + error.message, 'error');
        }
    }
    
    stopWebcam() {
        if (this.stream) {
            // Stop all tracks
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
            this.videoElement.srcObject = null;
            
            // Stop auto-capture
            this.stopAutoCapture();
            
            // End session
            this.endSession();
            
            console.log('Webcam stopped');
            this.updateUI('stopped');
            this.showNotification('Webcam stopped', 'info');
        }
    }
    
    startAutoCapture() {
        if (this.captureTimer) {
            clearInterval(this.captureTimer);
        }
        
        this.captureTimer = setInterval(() => {
            if (this.stream && !this.isCapturing) {
                this.captureAndPredict();
            }
        }, this.captureInterval);
        
        console.log('Auto-capture started');
    }
    
    stopAutoCapture() {
        if (this.captureTimer) {
            clearInterval(this.captureTimer);
            this.captureTimer = null;
            console.log('Auto-capture stopped');
        }
    }
    
    async captureAndPredict() {
        if (!this.stream || this.isCapturing) {
            return;
        }
        
        this.isCapturing = true;
        this.updateUI('capturing');
        
        try {
            // Capture frame from video
            const imageData = this.captureFrame();
            
            if (!imageData) {
                throw new Error('Failed to capture frame');
            }
            
            // Send to backend for prediction
            const result = await this.predictEmotion(imageData);
            
            // Display result
            this.displayResult(result);
            
            // Update session
            if (this.sessionId) {
                await this.updateSession(result.emotion);
            }
            
            // Add to history
            this.emotionHistory.push({
                emotion: result.emotion,
                confidence: result.confidence,
                timestamp: new Date()
            });
            
            this.predictionCount++;
            this.updateStats();
            
        } catch (error) {
            console.error('Error during capture and prediction:', error);
            this.showNotification('Prediction failed: ' + error.message, 'error');
        } finally {
            this.isCapturing = false;
            this.updateUI('ready');
        }
    }
    
    captureFrame() {
        try {
            // Get canvas context
            const context = this.canvasElement.getContext('2d');
            
            // Set canvas size to match video
            this.canvasElement.width = this.videoElement.videoWidth;
            this.canvasElement.height = this.videoElement.videoHeight;
            
            // Draw current video frame to canvas
            context.drawImage(
                this.videoElement,
                0, 0,
                this.canvasElement.width,
                this.canvasElement.height
            );
            
            // Convert to base64
            const imageData = this.canvasElement.toDataURL('image/jpeg', 0.8);
            
            return imageData;
            
        } catch (error) {
            console.error('Error capturing frame:', error);
            return null;
        }
    }
    
    async predictEmotion(imageData) {
        try {
            // Get CSRF token
            const csrfToken = this.getCsrfToken();
            
            // Send to backend
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    image: imageData,
                    notes: ''
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Prediction failed');
            }
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Prediction failed');
            }
            
            return result;
            
        } catch (error) {
            console.error('Error predicting emotion:', error);
            throw error;
        }
    }
    
    displayResult(result) {
        if (!this.resultContainer) return;
        
        // Create result HTML
        const html = `
            <div class="emotion-result-card animate-fade-in">
                <div class="emotion-header" style="background-color: ${result.color};">
                    <span class="emotion-emoji">${result.emoji}</span>
                    <h3 class="emotion-name">${result.emotion.toUpperCase()}</h3>
                </div>
                <div class="emotion-body">
                    <div class="confidence-bar">
                        <div class="confidence-label">Confidence</div>
                        <div class="progress">
                            <div class="progress-bar" role="progressbar" 
                                 style="width: ${result.confidence * 100}%; background-color: ${result.color};"
                                 aria-valuenow="${result.confidence * 100}" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                                ${(result.confidence * 100).toFixed(1)}%
                            </div>
                        </div>
                    </div>
                    <div class="emotion-probabilities mt-3">
                        <h6>All Emotions:</h6>
                        ${this.renderProbabilities(result.all_probabilities)}
                    </div>
                    <div class="prediction-meta mt-3">
                        <small class="text-muted">
                            Processing time: ${(result.processing_time * 1000).toFixed(0)}ms
                        </small>
                    </div>
                </div>
            </div>
        `;
        
        this.resultContainer.innerHTML = html;
    }
    
    renderProbabilities(probabilities) {
        let html = '<div class="probability-list">';
        
        // Sort by probability
        const sorted = Object.entries(probabilities).sort((a, b) => b[1] - a[1]);
        
        for (const [emotion, prob] of sorted) {
            const percentage = (prob * 100).toFixed(1);
            html += `
                <div class="probability-item">
                    <span class="emotion-label">${emotion}</span>
                    <div class="probability-bar">
                        <div class="probability-fill" style="width: ${percentage}%"></div>
                    </div>
                    <span class="probability-value">${percentage}%</span>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }
    
    async startSession() {
        try {
            const csrfToken = this.getCsrfToken();
            
            const response = await fetch('/face-emotion/api/start-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                this.sessionId = result.session_id;
                console.log('Session started:', this.sessionId);
            }
        } catch (error) {
            console.error('Error starting session:', error);
        }
    }
    
    async endSession() {
        if (!this.sessionId) return;
        
        try {
            const csrfToken = this.getCsrfToken();
            
            await fetch('/face-emotion/api/end-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
            
            console.log('Session ended:', this.sessionId);
            this.sessionId = null;
            
        } catch (error) {
            console.error('Error ending session:', error);
        }
    }
    
    async updateSession(emotion) {
        if (!this.sessionId) return;
        
        try {
            const csrfToken = this.getCsrfToken();
            
            await fetch('/face-emotion/api/update-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    emotion: emotion
                })
            });
            
        } catch (error) {
            console.error('Error updating session:', error);
        }
    }
    
    updateStats() {
        // Update prediction count
        const countElement = document.getElementById('predictionCount');
        if (countElement) {
            countElement.textContent = this.predictionCount;
        }
        
        // Update emotion distribution
        if (this.emotionHistory.length > 0) {
            this.updateEmotionChart();
        }
    }
    
    updateEmotionChart() {
        // Count emotions
        const emotionCounts = {};
        this.emotionHistory.forEach(item => {
            emotionCounts[item.emotion] = (emotionCounts[item.emotion] || 0) + 1;
        });
        
        // Update chart if exists
        const chartElement = document.getElementById('emotionChart');
        if (chartElement && typeof Chart !== 'undefined') {
            // Chart.js implementation would go here
            console.log('Emotion distribution:', emotionCounts);
        }
    }
    
    updateUI(state) {
        const startBtn = document.getElementById('startWebcam');
        const stopBtn = document.getElementById('stopWebcam');
        const captureBtn = document.getElementById('captureBtn');
        const statusElement = document.getElementById('webcamStatus');
        
        switch (state) {
            case 'started':
                if (startBtn) startBtn.disabled = true;
                if (stopBtn) stopBtn.disabled = false;
                if (captureBtn) captureBtn.disabled = false;
                if (statusElement) {
                    statusElement.innerHTML = '<span class="badge bg-success">Active</span>';
                }
                break;
                
            case 'stopped':
                if (startBtn) startBtn.disabled = false;
                if (stopBtn) stopBtn.disabled = true;
                if (captureBtn) captureBtn.disabled = true;
                if (statusElement) {
                    statusElement.innerHTML = '<span class="badge bg-secondary">Inactive</span>';
                }
                break;
                
            case 'capturing':
                if (captureBtn) {
                    captureBtn.disabled = true;
                    captureBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';
                }
                break;
                
            case 'ready':
                if (captureBtn) {
                    captureBtn.disabled = false;
                    captureBtn.innerHTML = '<i class="fas fa-camera"></i> Capture & Predict';
                }
                break;
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        notification.style.zIndex = '9999';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
    
    // Public methods
    getEmotionHistory() {
        return this.emotionHistory;
    }
    
    clearHistory() {
        this.emotionHistory = [];
        this.predictionCount = 0;
        this.updateStats();
    }
    
    exportHistory() {
        const data = JSON.stringify(this.emotionHistory, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `emotion_history_${new Date().toISOString()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the webcam page
    if (document.getElementById('webcamVideo')) {
        window.webcamDetector = new WebcamEmotionDetector({
            captureInterval: 2000,
            autoCapture: false
        });
        
        console.log('Webcam Emotion Detector initialized');
    }
});

// Made with Bob
