export type Role = "user" | "assistant";

export interface Message {
  role: Role;
  text: string;
  created_at: string;
}

export interface Demographics {
  age: number;
  gender: string;
  sexual_orientation: string;
  campus: string;
  travel_radius_km: number;
}

export interface PersonalityDimensions {
  extraversion: number;
  intuition: number;
  thinking: number;
  judging: number;
  neuroticism: number;
}

export interface Personality {
  mbti: string;
  dimensions: PersonalityDimensions;
}

export type DepthSignal = "low" | "medium" | "high";

export interface Interest {
  topic: string;
  depth_signal: DepthSignal;
  specific_details: string;
}

export interface Persona {
  session_id: string;
  summary: string;
  demographics: Demographics;
  personality: Personality;
  values_ranked: string[];
  interests: Interest[];
  dealbreakers: string[];
  conversation_hooks: string[];
  created_at: string;
}

export interface SessionCreateResponse {
  session_id: string;
  agent_messages: string[];
}

export interface MessageSendResponse {
  agent_messages: string[];
  complete: boolean;
}
