import { useEffect, useMemo, useRef } from "react";
import { IMessageBubble } from "./IMessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import type { Message } from "../types";

interface Props {
  messages: Message[];
  isTyping: boolean;
  typingLabel?: string;
}

const ONE_MINUTE_MS = 60_000;

function formatTimestamp(iso: string): string {
  const d = new Date(iso);
  const hours = d.getHours();
  const minutes = d.getMinutes().toString().padStart(2, "0");
  const period = hours >= 12 ? "PM" : "AM";
  const displayHour = ((hours + 11) % 12) + 1;
  const today = new Date();
  const isSameDay =
    d.getFullYear() === today.getFullYear() &&
    d.getMonth() === today.getMonth() &&
    d.getDate() === today.getDate();
  const dayLabel = isSameDay
    ? "Today"
    : d.toLocaleDateString(undefined, { weekday: "long" });
  return `${dayLabel} ${displayHour}:${minutes} ${period}`;
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

  // Index of the last user-authored message — used for the "Delivered" label.
  const lastUserIdx = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === "user") return i;
    }
    return -1;
  }, [messages]);

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto px-3 py-4"
    >
      {messages.map((m, i) => {
        const next = messages[i + 1];
        const prev = messages[i - 1];
        const isLastOfRun = !next || next.role !== m.role;

        // Render a timestamp separator before this message if the gap since
        // the prior one is > 1 minute (or if this is the very first message).
        let showTimestamp = false;
        if (!prev) {
          showTimestamp = true;
        } else {
          const gap = +new Date(m.created_at) - +new Date(prev.created_at);
          if (gap > ONE_MINUTE_MS) showTimestamp = true;
        }

        return (
          <div key={i}>
            {showTimestamp && (
              <div
                className="text-center text-[11px] text-gray-500 my-3 select-none"
                aria-hidden="true"
              >
                {formatTimestamp(m.created_at)}
              </div>
            )}
            <IMessageBubble
              role={m.role}
              text={m.text}
              isLastOfRun={isLastOfRun}
            />
            {/* "Delivered" under the last user message, iMessage-style */}
            {i === lastUserIdx && m.role === "user" && !isTyping && (
              <div className="text-right text-[10px] text-gray-500 mr-1 mb-1">
                Delivered
              </div>
            )}
          </div>
        );
      })}
      {isTyping && <TypingIndicator label={typingLabel} />}
      <div ref={bottomRef} />
    </div>
  );
}
