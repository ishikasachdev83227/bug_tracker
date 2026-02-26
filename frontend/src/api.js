// api.js centralizes API calls, token storage, auth header attachment, and normalized request errors.
const BASE_URL = "http://localhost:8000/api";

export function getToken() {
  return localStorage.getItem("issuehub_token");
}

export function setToken(token) {
  if (token) {
    localStorage.setItem("issuehub_token", token);
  } else {
    localStorage.removeItem("issuehub_token");
  }
}

export async function api(path, options = {}) {
  const headers = options.headers || {};
  if (!headers["Content-Type"] && options.body) {
    headers["Content-Type"] = "application/json";
  }
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let payload = null;
    try {
      payload = await res.json();
    } catch {
      payload = null;
    }
    const message = payload?.error?.message || `Request failed (${res.status})`;
    throw new Error(message);
  }
  if (res.status === 204) return null;
  return res.json();
}
