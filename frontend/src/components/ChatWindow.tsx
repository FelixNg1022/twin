import { useEffect, useRef } from "react";
import { IMessageBubble } from "./IMessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import type { Message } from "../types";

interface Props {
  messages: Message[];
  isTyping: boolean;
  typingLabel?: string;
}

export function ChatWindow({ messages, isTyping, typingLabel }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const userHasScrolledUp = useRef(false);

  useEffect(() => {
    if (!userHasScrolledUp.current) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isTyping]);

  const handleScroll = () => {
    const el = containerRef.current;
    if (!el) return;
    const distanceFromBottom =
      el.scrollHeight - (el.scrollTop + el.clientHeight);
    userHasScrolledUp.current = distanceFromBottom > 120;
  };

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto px-3 py-4"
    >
      {messages.map((m, i) => (
        <IMessageBubble key={i} role={m.role} text={m.text} />
      ))}
      {isTyping && <TypingIndicator label={typingLabel} />}
      <div ref={bottomRef} />
    </div>
  );
}
