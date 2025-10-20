/**
 * Vietnam Travel Assistant - Frontend JavaScript
 * Professional UI with smooth interactions
 */

class TravelAssistant {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.welcomeSection = document.getElementById('welcomeSection');
        this.charCount = document.getElementById('charCount');
        this.statusIndicator = document.getElementById('statusIndicator');
        
        this.isLoading = false;
        this.conversationStarted = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkHealth();
        this.loadConversationHistory();
        this.setupAutoResize();
    }
    
    setupEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter (but not Shift+Enter)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Character count
        this.messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.toggleSendButton();
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
        
        // Focus input on page load
        window.addEventListener('load', () => {
            this.messageInput.focus();
        });
    }
    
    setupAutoResize() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = count;
        
        if (count > 900) {
            this.charCount.style.color = '#e74c3c';
        } else if (count > 800) {
            this.charCount.style.color = '#f39c12';
        } else {
            this.charCount.style.color = '#999999';
        }
    }
    
    toggleSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isLoading;
        
        if (hasText && !this.isLoading) {
            this.sendButton.style.background = '#000000';
        } else {
            this.sendButton.style.background = '#404040';
        }
    }
    
    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.updateStatus('online', 'Online');
            } else {
                this.updateStatus('warning', 'Limited');
            }
        } catch (error) {
            this.updateStatus('offline', 'Offline');
            console.error('Health check failed:', error);
        }
    }
    
    updateStatus(status, text) {
        const statusDot = this.statusIndicator.querySelector('.status-dot');
        const statusText = this.statusIndicator.querySelector('span');
        
        statusDot.className = 'status-dot';
        statusDot.classList.add(`status-${status}`);
        statusText.textContent = text;
    }
    
    async loadConversationHistory() {
        try {
            const response = await fetch('/api/conversation');
            const messages = await response.json();
            
            if (messages.length > 0) {
                this.conversationStarted = true;
                this.hideWelcomeSection();
                
                messages.forEach(message => {
                    if (message.type === 'user') {
                        this.addUserMessage(message.message, false);
                    } else {
                        this.addAssistantMessage(message.message, message.sources, false);
                    }
                });
                
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Failed to load conversation history:', error);
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || this.isLoading) return;
        
        // Hide welcome section on first message
        if (!this.conversationStarted) {
            this.hideWelcomeSection();
            this.conversationStarted = true;
        }
        
        // Add user message to chat
        this.addUserMessage(message);
        
        // Clear input
        this.messageInput.value = '';
        this.updateCharCount();
        this.autoResizeTextarea();
        this.toggleSendButton();
        
        // Show loading
        this.showLoading();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.addAssistantMessage(data.response, data.sources);
            } else {
                this.addErrorMessage(data.error || 'Something went wrong. Please try again.');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addErrorMessage('Network error. Please check your connection and try again.');
        } finally {
            this.hideLoading();
            this.messageInput.focus();
        }
    }
    
    addUserMessage(message, animate = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-user ${animate ? 'animate' : ''}`;
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(message)}</div>
                <div class="message-meta">
                    <i class="fas fa-user"></i>
                    <span>${this.formatTime(new Date())}</span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addAssistantMessage(message, sources = null, animate = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-assistant ${animate ? 'animate' : ''}`;
        
        let sourcesHtml = '';
        if (sources && (sources.vector_results > 0 || sources.graph_results > 0)) {
            sourcesHtml = `
                <div class="sources-info">
                    ${sources.vector_results > 0 ? `
                        <div class="source-badge">
                            <i class="fas fa-search"></i>
                            <span>${sources.vector_results} destinations</span>
                        </div>
                    ` : ''}
                    ${sources.graph_results > 0 ? `
                        <div class="source-badge">
                            <i class="fas fa-project-diagram"></i>
                            <span>${sources.graph_results} connections</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.formatMessage(message)}</div>
                <div class="message-meta">
                    <i class="fas fa-robot"></i>
                    <span>${this.formatTime(new Date())}</span>
                </div>
                ${sourcesHtml}
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addErrorMessage(error) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message message-assistant animate';
        
        messageDiv.innerHTML = `
            <div class="message-content" style="border-left: 4px solid #e74c3c;">
                <div class="message-text">
                    <i class="fas fa-exclamation-triangle" style="color: #e74c3c; margin-right: 8px;"></i>
                    ${this.escapeHtml(error)}
                </div>
                <div class="message-meta">
                    <i class="fas fa-exclamation-circle"></i>
                    <span>${this.formatTime(new Date())}</span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showLoading() {
        this.isLoading = true;
        this.loadingIndicator.style.display = 'flex';
        this.toggleSendButton();
        this.scrollToBottom();
    }
    
    hideLoading() {
        this.isLoading = false;
        this.loadingIndicator.style.display = 'none';
        this.toggleSendButton();
    }
    
    hideWelcomeSection() {
        if (this.welcomeSection) {
            this.welcomeSection.style.display = 'none';
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }
    
    formatMessage(message) {
        // Convert markdown-like formatting to HTML
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/^- (.*$)/gim, '• $1')
            .replace(/^\d+\. (.*$)/gim, '<strong>$1</strong>');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    }
}

// Global functions for HTML onclick handlers
function sendExampleQuery(query) {
    const app = window.travelAssistant;
    app.messageInput.value = query;
    app.updateCharCount();
    app.toggleSendButton();
    app.sendMessage();
}

async function clearConversation() {
    if (confirm('Are you sure you want to start a new conversation? This will clear all messages.')) {
        try {
            await fetch('/api/clear');
            location.reload();
        } catch (error) {
            console.error('Failed to clear conversation:', error);
            alert('Failed to clear conversation. Please refresh the page.');
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.travelAssistant = new TravelAssistant();
});

// Add some additional CSS for status indicators
const additionalStyles = `
    .status-online { background-color: #00a86b; }
    .status-warning { background-color: #f39c12; }
    .status-offline { background-color: #e74c3c; }
    
    .message.animate {
        animation: fadeInUp 0.5s ease;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);