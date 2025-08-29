// EduVerse Platform Main JavaScript

// Global variables
let currentUser = null;
let notifications = [];
let chatMessages = [];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Main initialization function
function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize real-time updates
    initializeRealTimeUpdates();
    
    // Initialize chat functionality
    initializeChat();
    
    // Initialize notifications
    initializeNotifications();
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.querySelector('#search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            if (query.length >= 2) {
                performSearch(query);
            }
        }, 300));
    }
}

// Perform search
function performSearch(query) {
    const searchResults = document.querySelector('#search-results');
    if (!searchResults) return;
    
    // Show loading
    searchResults.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
    
    // Perform search request
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data, searchResults);
        })
        .catch(error => {
            console.error('Search error:', error);
            searchResults.innerHTML = '<div class="alert alert-danger">Ошибка поиска</div>';
        });
}

// Display search results
function displaySearchResults(data, container) {
    if (!data.results || data.results.length === 0) {
        container.innerHTML = '<div class="text-muted">Ничего не найдено</div>';
        return;
    }
    
    let html = '';
    data.results.forEach(result => {
        html += `
            <div class="search-result-item p-2 border-bottom">
                <a href="${result.url}" class="text-decoration-none">
                    <div class="fw-bold">${result.title}</div>
                    <div class="text-muted small">${result.description || ''}</div>
                </a>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Initialize real-time updates
function initializeRealTimeUpdates() {
    // Update dashboard stats every 30 seconds
    setInterval(updateDashboardStats, 30000);
    
    // Update notifications every minute
    setInterval(updateNotifications, 60000);
}

// Update dashboard statistics
function updateDashboardStats() {
    const dashboardStats = document.querySelector('#dashboard-stats');
    if (!dashboardStats) return;
    
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            updateStatsDisplay(data);
        })
        .catch(error => {
            console.error('Failed to update dashboard stats:', error);
        });
}

// Update statistics display
function updateStatsDisplay(stats) {
    Object.keys(stats).forEach(key => {
        const element = document.querySelector(`[data-stat="${key}"]`);
        if (element) {
            element.textContent = stats[key];
        }
    });
}

// Initialize chat functionality
function initializeChat() {
    const chatContainer = document.querySelector('.chat-container');
    if (!chatContainer) return;
    
    // Initialize chat input
    const chatInput = chatContainer.querySelector('.chat-input input');
    const sendButton = chatContainer.querySelector('.chat-input button');
    
    if (chatInput && sendButton) {
        // Send message on Enter key
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
        
        // Send message on button click
        sendButton.addEventListener('click', sendChatMessage);
    }
}

// Send chat message
function sendChatMessage() {
    const chatContainer = document.querySelector('.chat-container');
    const input = chatContainer.querySelector('.chat-input input');
    const message = input.value.trim();
    
    if (!message) return;
    
    const chatId = chatContainer.dataset.chatId;
    if (!chatId) return;
    
    // Add message to UI immediately
    addMessageToUI({
        content: message,
        sender: 'me',
        timestamp: new Date().toISOString()
    });
    
    // Clear input
    input.value = '';
    
    // Send to server
    fetch(`/api/chat/${chatId}/send`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `message=${encodeURIComponent(message)}`
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            showToast('Ошибка', 'Не удалось отправить сообщение', 'error');
        }
    })
    .catch(error => {
        console.error('Failed to send message:', error);
        showToast('Ошибка', 'Не удалось отправить сообщение', 'error');
    });
}

// Add message to UI
function addMessageToUI(message) {
    const chatMessages = document.querySelector('.chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${message.sender === 'me' ? 'sent' : 'received'}`;
    
    const time = new Date(message.timestamp).toLocaleTimeString();
    
    messageElement.innerHTML = `
        <div class="message-content">${message.content}</div>
        <div class="message-time">${time}</div>
    `;
    
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Initialize notifications
function initializeNotifications() {
    // Load initial notifications
    loadNotifications();
    
    // Set up notification polling
    setInterval(loadNotifications, 60000); // Check every minute
}

// Load notifications
function loadNotifications() {
    fetch('/api/notifications?per_page=5')
        .then(response => response.json())
        .then(data => {
            notifications = data.notifications;
            updateNotificationDisplay();
            updateNotificationCount();
        })
        .catch(error => {
            console.error('Failed to load notifications:', error);
        });
}

// Update notification display
function updateNotificationDisplay() {
    const container = document.querySelector('#notifications-list');
    if (!container) return;
    
    if (notifications.length === 0) {
        container.innerHTML = '<li><span class="dropdown-item-text text-muted">Нет уведомлений</span></li>';
        return;
    }
    
    let html = '';
    notifications.slice(0, 5).forEach(notification => {
        const unreadClass = notification.is_read ? '' : 'unread';
        const iconClass = getNotificationIcon(notification.type);
        
        html += `
            <li class="notification-item ${unreadClass}">
                <a class="dropdown-item" href="#" onclick="markNotificationRead(${notification.id})">
                    <i class="${iconClass} me-2"></i>
                    <div>
                        <div class="fw-bold">${notification.title}</div>
                        <div class="small text-muted">${notification.message}</div>
                        <div class="small text-muted">${formatTimeAgo(notification.created_at)}</div>
                    </div>
                </a>
            </li>
        `;
    });
    
    container.innerHTML = html;
}

// Update notification count
function updateNotificationCount() {
    const badge = document.querySelector('#unread-notification-count');
    if (!badge) return;
    
    const unreadCount = notifications.filter(n => !n.is_read).length;
    
    if (unreadCount > 0) {
        badge.textContent = unreadCount;
        badge.style.display = 'inline';
    } else {
        badge.style.display = 'none';
    }
}

// Mark notification as read
function markNotificationRead(notificationId) {
    fetch(`/api/notifications/${notificationId}/read`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update local notification
            const notification = notifications.find(n => n.id === notificationId);
            if (notification) {
                notification.is_read = true;
                updateNotificationDisplay();
                updateNotificationCount();
            }
        }
    })
    .catch(error => {
        console.error('Failed to mark notification as read:', error);
    });
}

// Get notification icon class
function getNotificationIcon(type) {
    const icons = {
        'info': 'fas fa-info-circle',
        'warning': 'fas fa-exclamation-triangle',
        'error': 'fas fa-times-circle',
        'success': 'fas fa-check-circle'
    };
    return icons[type] || 'fas fa-bell';
}

// Format time ago
function formatTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = now - time;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Только что';
    if (minutes < 60) return `${minutes} мин. назад`;
    if (hours < 24) return `${hours} ч. назад`;
    if (days < 7) return `${days} дн. назад`;
    
    return time.toLocaleDateString();
}

// Show toast notification
function showToast(title, message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong><br>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Create toast container
function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// Utility function: debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Utility function: format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Utility function: format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Utility function: format time
function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export functions for global use
window.EduVerse = {
    showToast,
    formatFileSize,
    formatDate,
    formatTime,
    updateNotificationCount,
    markNotificationRead
};