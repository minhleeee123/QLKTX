// Enhanced Notification System - Hybrid Approach
class NotificationSystem {
    constructor() {
        this.container = this.createContainer();
        this.init();
    }

    init() {
        // Auto-convert existing Flask flash messages to JavaScript notifications
        this.convertFlashMessages();
        
        // Listen for custom notification events
        document.addEventListener('notification', (event) => {
            this.show(event.detail.type, event.detail.message, event.detail.options);
        });
    }

    createContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1055;
                max-width: 400px;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    convertFlashMessages() {
        // Convert Flask flash messages to JavaScript notifications
        const flashMessages = document.querySelectorAll('.alert[role="alert"]');
        flashMessages.forEach(flash => {
            const isError = flash.classList.contains('alert-danger');
            const isSuccess = flash.classList.contains('alert-success');
            const isWarning = flash.classList.contains('alert-warning');
            const isInfo = flash.classList.contains('alert-info');
            
            let type = 'info';
            if (isError) type = 'error';
            else if (isSuccess) type = 'success';
            else if (isWarning) type = 'warning';
            
            const message = flash.textContent.trim();
            if (message) {
                // Remove the original flash message
                flash.remove();
                // Show as JavaScript notification
                this.show(type, message, { 
                    duration: 6000,
                    animate: true,
                    dismissible: true 
                });
            }
        });
    }

    show(type, message, options = {}) {
        const defaults = {
            duration: 5000,
            animate: true,
            dismissible: true,
            position: 'top-right',
            showProgress: true
        };
        
        const config = { ...defaults, ...options };
        const notification = this.createNotification(type, message, config);
        
        this.container.appendChild(notification);
        
        // Animate in
        if (config.animate) {
            setTimeout(() => {
                notification.classList.add('show');
            }, 10);
        }
        
        // Auto remove
        if (config.duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, config.duration);
        }
        
        return notification;
    }

    createNotification(type, message, config) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            margin-bottom: 10px;
            padding: 16px;
            max-width: 100%;
            transform: translateX(100%);
            transition: all 0.3s ease;
            pointer-events: auto;
            border-left: 4px solid ${this.getTypeColor(type)};
            opacity: 0;
        `;

        const icon = this.getTypeIcon(type);
        const progressBar = config.showProgress ? this.createProgressBar(config.duration) : '';
        
        notification.innerHTML = `
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <div style="color: ${this.getTypeColor(type)}; font-size: 18px; margin-top: 2px;">
                    <i class="fas fa-${icon}"></i>
                </div>
                <div style="flex: 1;">
                    <div style="color: #333; font-weight: 500; margin-bottom: 4px;">
                        ${this.getTypeTitle(type)}
                    </div>
                    <div style="color: #666; font-size: 14px; line-height: 1.4;">
                        ${message}
                    </div>
                    ${progressBar}
                </div>
                ${config.dismissible ? `
                    <button onclick="notificationSystem.remove(this.parentElement.parentElement)" 
                            style="background: none; border: none; color: #999; cursor: pointer; padding: 0; font-size: 16px;">
                        <i class="fas fa-times"></i>
                    </button>
                ` : ''}
            </div>
        `;

        // Add show class for animation
        notification.classList.add('notification-enter');
        
        return notification;
    }

    createProgressBar(duration) {
        if (duration <= 0) return '';
        
        return `
            <div style="margin-top: 8px; background: #f0f0f0; height: 2px; border-radius: 1px; overflow: hidden;">
                <div style="height: 100%; background: currentColor; width: 100%; 
                           animation: notificationProgress ${duration}ms linear forwards;"></div>
            </div>
        `;
    }

    remove(notification) {
        if (!notification || !notification.parentNode) return;
        
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }

    getTypeColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        return colors[type] || colors.info;
    }

    getTypeIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }

    getTypeTitle(type) {
        const titles = {
            success: 'Thành công',
            error: 'Lỗi',
            warning: 'Cảnh báo',
            info: 'Thông tin'
        };
        return titles[type] || titles.info;
    }

    // Convenience methods
    success(message, options) {
        return this.show('success', message, options);
    }

    error(message, options) {
        return this.show('error', message, options);
    }

    warning(message, options) {
        return this.show('warning', message, options);
    }

    info(message, options) {
        return this.show('info', message, options);
    }
}

// CSS Animation for progress bar
const style = document.createElement('style');
style.textContent = `
    @keyframes notificationProgress {
        from { width: 100%; }
        to { width: 0%; }
    }
    
    .notification.show {
        transform: translateX(0) !important;
        opacity: 1 !important;
    }
    
    .notification:hover .progress-bar {
        animation-play-state: paused;
    }
`;
document.head.appendChild(style);

// Initialize the notification system
const notificationSystem = new NotificationSystem();

// Global helper functions
window.showNotification = (type, message, options) =>
  notificationSystem.show(type, message, options);
window.showSuccess = (message, options) => notificationSystem.success(message, options);
window.showError = (message, options) => notificationSystem.error(message, options);
window.showWarning = (message, options) => notificationSystem.warning(message, options);
window.showInfo = (message, options) => notificationSystem.info(message, options);
