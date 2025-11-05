import { useState, useEffect } from "react";
import api from "../lib/axios";
import { useNavigate } from "react-router-dom";

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

const login = async (email: string, password: string) => {
  console.log("Calling /auth/login");
  try {
    const res = await api.post("/auth/login", { email, password });
    console.log("Login response:", res); // 👈 see what we got back
    // adjust depending on backend response shape
    setUser(res.data.user ?? res.data);
    return res.data;
  } catch (err) {
    console.error("Login error:", err); // 👈 this is what we want to see
    throw err;
  }
};


  const logout = async () => {
    await api.post("/auth/logout");
    setUser(null);
    navigate("/login");
  };

  return { user, loading, login, logout };
}
