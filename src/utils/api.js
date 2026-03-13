import { auth } from "../firebase";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export const getApiUrl = (endpoint) => {
  return API_BASE_URL ? `${API_BASE_URL}${endpoint}` : endpoint;
};

const getFreshToken = async () => {
  if (auth.currentUser) {
    return await auth.currentUser.getIdToken();
  }
  return localStorage.getItem("authToken");
};

export const apiCall = async (endpoint, options = {}) => {
  try {
    const token = await getFreshToken();

    const headers = {
      ...options.headers,
      ...(token && { Authorization: `Bearer ${token}` }),
    };

    const response = await fetch(getApiUrl(endpoint), {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem("authToken");
        localStorage.removeItem("user");
        if (window.location.pathname !== "/") {
          window.location.href = "/";
        }
      }
      const errorData = await response.json();
      throw new Error(errorData.detail || `API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API call failed:", error);
    throw error;
  }
};

export default API_BASE_URL;
