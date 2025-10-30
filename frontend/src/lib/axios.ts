import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  withCredentials: true, // send cookies
});

api.interceptors.request.use((config) => {
  const csrf = localStorage.getItem("csrf_token");
  if (csrf) config.headers["X-CSRF-Token"] = csrf;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      // Optionally trigger logout or redirect
      console.warn("Unauthorized – consider redirect to /login");
    }
    return Promise.reject(err);
  }
);

export default api;
