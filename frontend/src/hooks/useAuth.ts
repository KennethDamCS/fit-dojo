import { useState, useEffect } from "react";
import api from "../lib/axios";
import { useNavigate } from "react-router-dom";

// Shape of the user coming back from /auth/me
export type AuthUser = {
  id: number;
  email: string;
  // add anything else your backend returns if you want:
  // is_verified?: boolean;
  // created_at?: string;
  // updated_at?: string;
};

// Backend might return either the user directly or wrapped in { user: ... }
export type LoginResponse = AuthUser | { user: AuthUser };

// What the hook returns to consumers (Dashboard, etc.)
export type UseAuthResult = {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<LoginResponse>;
  logout: () => Promise<void>;
};

export function useAuth(): UseAuthResult {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;

    api
      .get<AuthUser>("/auth/me")
      .then((res) => {
        if (!cancelled) setUser(res.data);
      })
      .catch(() => {
        if (!cancelled) setUser(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const login = async (email: string, password: string): Promise<LoginResponse> => {
    // console.log("Calling /auth/login"); was used for testing
    try {
      const res = await api.post<LoginResponse>("/auth/login", { email, password });

      const data = res.data;
      const nextUser: AuthUser = "user" in data ? data.user : data;

      setUser(nextUser);
      return data;
    } catch (err: unknown) {
      console.error("Login error:", err);
      throw err;
    }
  };

  const logout = async (): Promise<void> => {
    await api.post("/auth/logout");
    setUser(null);
    navigate("/login");
  };

  return { user, loading, login, logout };
}
