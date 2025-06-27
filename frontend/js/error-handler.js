// frontend/js/error-handler.js
export class ErrorHandler {
  static showError(message, duration = 5000) {
    const existingError = document.getElementById('global-error');
    if (existingError) existingError.remove();

    const errorElement = document.createElement('div');
    errorElement.id = 'global-error';
    errorElement.style.position = 'fixed';
    errorElement.style.bottom = '20px';
    errorElement.style.right = '20px';
    errorElement.style.padding = '15px 20px';
    errorElement.style.backgroundColor = '#ff4b2b';
    errorElement.style.color = 'white';
    errorElement.style.borderRadius = '8px';
    errorElement.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    errorElement.style.zIndex = '1000';
    errorElement.style.maxWidth = '400px';
    errorElement.style.animation = 'fadeIn 0.3s ease-out';
    errorElement.textContent = message;

    document.body.appendChild(errorElement);

    setTimeout(() => {
      errorElement.style.animation = 'fadeOut 0.3s ease-out';
      setTimeout(() => errorElement.remove(), 300);
    }, duration);
  }
}