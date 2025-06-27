class AlertSystem {
  static queue = [];
  static isShowing = false;

  static show(message, type = 'info', duration = 5000) {
    const alertId = Date.now();
    this.queue.push({ message, type, duration, alertId });
    
    if (!this.isShowing) {
      this._showNext();
    }
  }

  static _showNext() {
    if (this.queue.length === 0) {
      this.isShowing = false;
      return;
    }

    this.isShowing = true;
    const { message, type, duration, alertId } = this.queue.shift();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.setAttribute('role', 'alert');
    alert.setAttribute('aria-live', 'assertive');
    alert.dataset.alertId = alertId;
    
    alert.innerHTML = `
      <span>${message}</span>
      <button class="alert-close" aria-label="Close alert">&times;</button>
    `;
    
    document.body.appendChild(alert);
    
    // Force reflow to enable animation
    void alert.offsetWidth;
    
    alert.classList.add('show');
    
    // Close button event
    alert.querySelector('.alert-close').addEventListener('click', () => {
      this._hideAlert(alert);
    });
    
    // Auto-hide if duration is set
    if (duration > 0) {
      setTimeout(() => {
        if (document.body.contains(alert)) {
          this._hideAlert(alert);
        }
      }, duration);
    }
  }

  static _hideAlert(alert) {
    alert.style.animation = 'fadeOut 0.3s forwards';
    setTimeout(() => {
      if (document.body.contains(alert)) {
        alert.remove();
      }
      this._showNext();
    }, 300);
  }

  static success(message, duration = 5000) {
    this.show(message, 'success', duration);
  }

  static error(message, duration = 5000) {
    this.show(message, 'error', duration);
  }

  static warning(message, duration = 5000) {
    this.show(message, 'warning', duration);
  }

  static info(message, duration = 3000) {
    this.show(message, 'info', duration);
  }

  static clearAll() {
    document.querySelectorAll('.alert').forEach(alert => {
      alert.remove();
    });
    this.queue = [];
    this.isShowing = false;
  }
}

// Initialize globally
window.Alert = AlertSystem;

// Global error handler
window.addEventListener('unhandledrejection', event => {
  Alert.error(event.reason?.message || 'An unexpected error occurred');
});

window.addEventListener('error', (event) => {
  Alert.error(event.message || 'Script error occurred');
});