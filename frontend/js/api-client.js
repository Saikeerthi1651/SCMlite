/**
 * Enhanced API Client with Alert Integration
 */
class ApiClient {
  constructor() {
    this.baseUrl = window.location.origin.includes('localhost') 
      ? 'http://localhost:8000' 
      : 'http://51.21.139.239:8000';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }

  async _handleResponse(response) {
    const contentType = response.headers.get('content-type');
    let data;
    
    try {
      data = contentType?.includes('application/json') 
        ? await response.json() 
        : await response.text();
    } catch (error) {
      throw new Error('Failed to parse response');
    }

    // Show alert if specified in response
    if (data?.alert) {
      const { type, message } = data.alert;
      Alert[type](message);
    }

    if (!response.ok) {
      const error = new Error(data?.message || 'Request failed');
      error.response = data;
      throw error;
    }

    return data;
  }

  async request(endpoint, options = {}) {
    const headers = {
      ...this.defaultHeaders,
      ...options.headers
    };

    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers,
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      if (!error.message.includes('Failed to parse')) {
        Alert.error(error.message || 'Network error');
      }
      throw error;
    }
  }

  // Auth methods
  async login(email, password, recaptchaToken = null) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        username: email,
        password,
        recaptcha_token: recaptchaToken
      })
    });
  }

  async logout() {
    return this.request('/auth/logout', {
      method: 'POST'
    });
  }

  // Shipment methods
  async getShipments() {
    return this.request('/shipment/search_shipments');
  }

  async createShipment(shipmentData) {
    return this.request('/shipment/create_shipment', {
      method: 'POST',
      body: JSON.stringify(shipmentData)
    });
  }

  // User methods
  async getCurrentUser() {
    return this.request('/auth/me');
  }
}

export const apiClient = new ApiClient();