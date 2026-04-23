import type {
  MessageSendResponse,
  Persona,
  SessionCreateResponse,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function createSession(): Promise<SessionCreateResponse> {
  const res = await fetch(`${API_BASE}/sessions`, { method: "POST" });
  if (!res.ok) throw new Error(`createSession failed: ${res.status}`);
  return res.json();
}

export async function sendMessage(
  sessionId: string,
  text: string,
): Promise<MessageSendResponse> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`sendMessage failed: ${res.status}`);
  return res.json();
}

export async function fetchPersona(sessionId: string): Promise<Persona> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/persona`);
  if (!res.ok) throw new Error(`fetchPersona failed: ${res.status}`);
  return res.json();
}
