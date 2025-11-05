import axios from "axios";

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()!.split(";").shift() || null;
  return null;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const csrf = getCookie("fd_csrf")
  if (csrf) {
    config.headers["X-CSRF-Token"] = csrf;
  }
  return config;
});

api.interceptors.response.use(
  (res) => {
    const csrf =
      (res.headers["x-csrf-token"] as string | undefined) ??
      (res.headers["X-CSRF-Token"] as string | undefined);

    if (csrf) {
      localStorage.setItem("csrf_token", csrf);
    }

    return res;
  },
  (err) => {
    if (err.response?.status === 401) {
      console.warn("Unauthorized – consider redirect to /login");
    }
    return Promise.reject(err);
  }
);

export default api;
