import param from 'jquery-param';

/**
 * Utility for making XHR calls from all our supported browsers.
 *
 * Also handles csrf and known response types.
 */
export class MyJobsApi {
  constructor(csrf) {
    this.csrf = csrf;
  }

  async checkStatus(response) {
    if (response.status === 200) {
      return response;
    }

    const error = new Error(response.statusText);
    error.response = response;
    if (response.headers.get('content-type') === 'application/json') {
      error.data = await response.json();
    }
    throw error;
  }

  parseJSON(response) {
    return response.json();
  }

  async get(url) {
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/json',
      },
    });
    return this.parseJSON(await this.checkStatus(response));
  }

  async ajaxWithFormData(method, url, data) {
    const formData = param(data);
    const response = await fetch(url, {
      method: method,
      body: formData,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': this.csrf,
        'Accept': 'application/json',
      },
    });
    return this.parseJSON(await this.checkStatus(response));
  }

  async post(url, data) {
    return this.ajaxWithFormData('POST', url, data);
  }

  async delete(url, data) {
    return this.ajaxWithFormData('DELETE', url, data);
  }

  /** Upload data to a server by submitting the contents of :data: as
   * multi-part form data.
   */
  async upload(url, data) {
    const formData = new FormData();
    // passing an anonymous function within a for loop makes multiple function
    // references, which is undesirable
    const assignValue = key => value => formData.append(key, value);

    for (const key in data) {
      if (data.hasOwnProperty(key)) {
        if (Array.isArray(data[key])) {
          data[key].forEach(assignValue(key));
        } else {
          formData.append(key, data[key]);
        }
      }
    }

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      credentials: 'include',
      headers: {
        'X-CSRFToken': this.csrf,
      },
    });

    return this.parseJSON(await this.checkStatus(response));
  }
}

export function isClientError(exc) {
  return Boolean(exc.response) && exc.response.status === 400;
}

export function errorData(exc) {
  return exc.data;
}
