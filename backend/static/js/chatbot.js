/**
 * AI Wellness Chatbot - Main JavaScript
 * Handles all chatbot interactions, API calls, and UI updates
 */

// Global variables
let chatbotOpen = false;
let currentSessionId = null;
let messageQueue = [];
let isTyping = false;

// Initialize chatbot on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeChatbot();
    loadCurrentEmotion();
    checkForUnreadMessages();
});

/**
 * Initialize chatbot widget
 */
function initializeChatbot() {
    // Check if user is authenticated
    if (!isUserAuthenticated()) {
        return;
    }
    
    // Load existing session or create new one
    loadOrCreateSession();
    
    // Set up event listeners
    setupEventListeners();
    
    // Auto-open if there's an active session with recent activity
    checkAutoOpen();
}

/**
 * Check if user is authenticated
 */
function isUserAuthenticated() {
    // Check if user data exists in the page
    return document.body.dataset.userId !== undefined;
}

/**
 * Toggle chatbot window
 */
function toggleChatbot() {
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotToggle = document.getElementById('chatbot-toggle');
    
    if (chatbotOpen) {
        closeChatbot();
    } else {
        openChatbot();
    }
}

/**
 * Open chatbot window
 */
function openChatbot() {
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotToggle = document.getElementById('chatbot-toggle');
    
    chatbotWindow.style.display = 'flex';
    chatbotToggle.style.display = 'none';
    chatbotOpen = true;
    
    // Focus on input
    document.getElementById('chat-input').focus();
    
    // Mark messages as read
    markMessagesAsRead();
    
    // Scroll to bottom
    scrollToBottom();
    
    // Load latest emotion
    loadCurrentEmotion();
}

/**
 * Close chatbot window
 */
function closeChatbot() {
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotToggle = document.getElementById('chatbot-toggle');
    
    chatbotWindow.style.display = 'none';
    chatbotToggle.style.display = 'flex';
    chatbotOpen = false;
}

/**
 * Minimize chatbot window
 */
function minimizeChatbot() {
    closeChatbot();
}

/**
 * Send message to chatbot
 */
async function sendMessage(event) {
    if (event) {
        event.preventDefault();
    }
    
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) {
        return;
    }
    
    // Clear input
    input.value = '';
    
    // Add user message to UI
    addMessageToUI(message, true);
    
    // Hide quick suggestions
    hideQuickSuggestions();
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send message to backend
        const response = await fetch('/chatbot/api/send-message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update session ID
            currentSessionId = data.session_id;
            
            // Hide typing indicator
            hideTypingIndicator();
            
            // Add bot response to UI
            addMessageToUI(data.response, false, data.emotion_context);
            
            // Check for emergency alert
            if (data.emergency_alert) {
                showEmergencyAlert(data.emergency_alert);
            }
            
            // Update emotion display
            if (data.current_emotion) {
                updateEmotionDisplay(data.current_emotion);
            }
        } else {
            hideTypingIndicator();
            addMessageToUI('Sorry, I encountered an error. Please try again.', false);
        }
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        addMessageToUI('Sorry, I\'m having trouble connecting. Please check your internet connection.', false);
    }
}

/**
 * Send quick message
 */
function sendQuickMessage(message) {
    document.getElementById('chat-input').value = message;
    sendMessage();
}

/**
 * Add message to UI
 */
function addMessageToUI(message, isUser, emotionContext = null) {
    const messagesContainer = document.getElementById('chatbot-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = `<i class="fas fa-${isUser ? 'user' : 'robot'}"></i>`;
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    // Parse message for formatting
    const formattedMessage = formatMessage(message);
    bubble.innerHTML = formattedMessage;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = 'Just now';
    
    content.appendChild(bubble);
    content.appendChild(time);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    scrollToBottom();
}

/**
 * Format message with HTML
 */
function formatMessage(message) {
    // Convert line breaks
    message = message.replace(/\n/g, '<br>');
    
    // Convert bold text
    message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert bullet points
    message = message.replace(/^- (.+)$/gm, '<li>$1</li>');
    if (message.includes('<li>')) {
        message = '<ul>' + message + '</ul>';
    }
    
    return message;
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    indicator.style.display = 'block';
    isTyping = true;
    scrollToBottom();
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    indicator.style.display = 'none';
    isTyping = false;
}

/**
 * Scroll messages to bottom
 */
function scrollToBottom() {
    const messagesContainer = document.getElementById('chatbot-messages');
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
}

/**
 * Load or create chat session
 */
async function loadOrCreateSession() {
    try {
        const response = await fetch('/chatbot/api/get-or-create-session/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSessionId = data.session_id;
            
            // Load recent messages if session exists
            if (data.messages && data.messages.length > 0) {
                loadRecentMessages(data.messages);
            }
        }
    } catch (error) {
        console.error('Error loading session:', error);
    }
}

/**
 * Load recent messages
 */
function loadRecentMessages(messages) {
    const messagesContainer = document.getElementById('chatbot-messages');
    
    // Clear welcome message if there are existing messages
    if (messages.length > 0) {
        messagesContainer.innerHTML = '';
    }
    
    messages.forEach(msg => {
        addMessageToUI(msg.message, msg.is_user_message, msg.emotion_context);
    });
}

/**
 * Load current emotion
 */
async function loadCurrentEmotion() {
    try {
        const response = await fetch('/chatbot/api/latest-emotion/');
        const data = await response.json();
        
        if (data.success) {
            updateEmotionDisplay(data);
        }
    } catch (error) {
        console.error('Error loading emotion:', error);
    }
}

/**
 * Update emotion display
 */
function updateEmotionDisplay(emotionData) {
    const badge = document.getElementById('current-emotion-badge');
    
    if (!badge) return;
    
    const emotionColors = {
        'happy': '#ffc107',
        'sad': '#6c757d',
        'angry': '#dc3545',
        'stressed': '#fd7e14',
        'excited': '#ff69b4',
        'relaxed': '#28a745',
        'anxious': '#fd7e14',
        'neutral': '#6c757d'
    };
    
    const color = emotionColors[emotionData.emotion] || '#6c757d';
    
    badge.innerHTML = `
        <span style="background: ${color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">
            ${emotionData.emotion.charAt(0).toUpperCase() + emotionData.emotion.slice(1)}
        </span>
    `;
}

/**
 * Show emotion picker
 */
function showEmotionPicker() {
    const picker = document.getElementById('emotion-picker');
    picker.style.display = 'block';
}

/**
 * Hide emotion picker
 */
function hideEmotionPicker() {
    const picker = document.getElementById('emotion-picker');
    picker.style.display = 'none';
}

/**
 * Select emotion from picker
 */
function selectEmotion(emotion, emoji) {
    const input = document.getElementById('chat-input');
    input.value = `I'm feeling ${emotion} ${emoji}`;
    hideEmotionPicker();
    input.focus();
}

/**
 * Hide quick suggestions
 */
function hideQuickSuggestions() {
    const suggestions = document.getElementById('quick-suggestions');
    if (suggestions) {
        suggestions.style.display = 'none';
    }
}

/**
 * Check for unread messages
 */
async function checkForUnreadMessages() {
    try {
        const response = await fetch('/chatbot/api/unread-count/');
        const data = await response.json();
        
        if (data.success && data.count > 0) {
            showUnreadBadge(data.count);
        }
    } catch (error) {
        console.error('Error checking unread messages:', error);
    }
}

/**
 * Show unread badge
 */
function showUnreadBadge(count) {
    const badge = document.getElementById('unread-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = 'flex';
    }
}

/**
 * Mark messages as read
 */
async function markMessagesAsRead() {
    try {
        await fetch('/chatbot/api/mark-read/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const badge = document.getElementById('unread-badge');
        if (badge) {
            badge.style.display = 'none';
        }
    } catch (error) {
        console.error('Error marking messages as read:', error);
    }
}

/**
 * Show emergency alert
 */
function showEmergencyAlert(alertData) {
    const modal = new bootstrap.Modal(document.getElementById('emergencyModal'));
    modal.show();
}

/**
 * Start breathing exercise
 */
function startBreathingExercise() {
    // Close emergency modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('emergencyModal'));
    modal.hide();
    
    // Send message to chatbot
    document.getElementById('chat-input').value = 'Start breathing exercise';
    sendMessage();
}

/**
 * Get emergency support
 */
function getEmergencySupport() {
    // Close emergency modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('emergencyModal'));
    modal.hide();
    
    // Send message to chatbot
    document.getElementById('chat-input').value = 'I need emergency support';
    sendMessage();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Enter key to send message
    const input = document.getElementById('chat-input');
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Auto-resize input
    if (input) {
        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
}

/**
 * Check if chatbot should auto-open
 */
async function checkAutoOpen() {
    try {
        const response = await fetch('/chatbot/api/should-auto-open/');
        const data = await response.json();
        
        if (data.success && data.should_open) {
            setTimeout(() => {
                openChatbot();
            }, 2000);
        }
    } catch (error) {
        console.error('Error checking auto-open:', error);
    }
}

/**
 * Get recommendations
 */
async function getRecommendations() {
    try {
        const response = await fetch('/chatbot/api/latest-emotion/');
        const emotionData = await response.json();
        
        if (emotionData.success) {
            const recResponse = await fetch(`/chatbot/api/recommendations/?emotion=${emotionData.emotion}`);
            const recData = await recResponse.json();
            
            if (recData.success) {
                displayRecommendationsModal(recData.recommendations);
            }
        }
    } catch (error) {
        console.error('Error getting recommendations:', error);
    }
}

/**
 * Display recommendations in modal
 */
function displayRecommendationsModal(recommendations) {
    // Create modal dynamically
    let modalHTML = `
        <div class="modal fade" id="recommendationsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-lightbulb"></i> Wellness Recommendations
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
    `;
    
    recommendations.forEach(rec => {
        modalHTML += `
            <div class="col-md-6 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <h6 class="card-title">${rec.title}</h6>
                        <p class="card-text">${rec.description}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-clock"></i> ${rec.duration} min
                            </small>
                            <button class="btn btn-sm btn-primary" onclick="startActivity('${rec.type}', '${rec.title}')">
                                Start
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    modalHTML += `
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('recommendationsModal'));
    modal.show();
    
    // Remove modal after closing
    document.getElementById('recommendationsModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Export functions for global access
 */
window.toggleChatbot = toggleChatbot;
window.openChatbot = openChatbot;
window.closeChatbot = closeChatbot;
window.minimizeChatbot = minimizeChatbot;
window.sendMessage = sendMessage;
window.sendQuickMessage = sendQuickMessage;
window.showEmotionPicker = showEmotionPicker;
window.hideEmotionPicker = hideEmotionPicker;
window.selectEmotion = selectEmotion;
window.startBreathingExercise = startBreathingExercise;
window.getEmergencySupport = getEmergencySupport;
window.getRecommendations = getRecommendations;
window.getCookie = getCookie;

// Made with Bob
