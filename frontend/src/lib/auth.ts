import api from "./axios";

export interface Session {
  id: number;
  created_at: string;
  last_seen_at: string | null;
  ip_address: string | null;
  user_agent: string | null;
  is_current: boolean;
}

export async function getSessions(): Promise<Session[]> {
  const res = await api.get<Session[]>("/auth/sessions");
  return res.data;
}

export async function revokeAllSessions(): Promise<void> {
  await api.post("/auth/logout-all");
}