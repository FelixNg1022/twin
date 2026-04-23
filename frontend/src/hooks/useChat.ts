import { useCallback, useEffect, useRef, useState } from "react";
import { createSession, fetchPersona, sendMessage } from "../api";
import type { Message, Persona } from "../types";

export interface UseChatState {
  messages: Message[];
  isTyping: boolean;
  complete: boolean;
  persona: Persona | null;
  sessionId: string | null;
  send: (text: string) => Promise<void>;
  reset: () => Promise<void>;
}

export function useChat(): UseChatState {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [complete, setComplete] = useState(false);
  const [persona, setPersona] = useState<Persona | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const bootstrapped = useRef(false);

  const bootstrap = useCallback(async () => {
    setIsTyping(true);
    try {
      const res = await createSession();
      setSessionId(res.session_id);
      const initialAssistant: Message[] = res.agent_messages.map((text) => ({
        role: "assistant",
        text,
        created_at: new Date().toISOString(),
      }));
      setMessages(initialAssistant);
    } catch (e) {
      alert("something went wrong starting the chat, refresh to retry");
      console.error(e);
    } finally {
      setIsTyping(false);
    }
  }, []);

  useEffect(() => {
    if (bootstrapped.current) return;
    bootstrapped.current = true;
    void bootstrap();
  }, [bootstrap]);

  const send = useCallback(
    async (text: string) => {
      if (!sessionId || isTyping) return;
      const userMsg: Message = {
        role: "user",
        text,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsTyping(true);
      try {
        const res = await sendMessage(sessionId, text);
        const agentMsgs: Message[] = res.agent_messages.map((t) => ({
          role: "assistant",
          text: t,
          created_at: new Date().toISOString(),
        }));
        setMessages((prev) => [...prev, ...agentMsgs]);
        setComplete(res.complete);
        if (res.complete && sessionId) {
          const p = await fetchPersona(sessionId);
          setPersona(p);
        }
      } catch (e) {
        alert("something went wrong, try again");
        console.error(e);
      } finally {
        setIsTyping(false);
      }
    },
    [sessionId, isTyping],
  );

  const reset = useCallback(async () => {
    setMessages([]);
    setComplete(false);
    setPersona(null);
    setSessionId(null);
    bootstrapped.current = false;
    await bootstrap();
  }, [bootstrap]);

  return { messages, isTyping, complete, persona, sessionId, send, reset };
}
