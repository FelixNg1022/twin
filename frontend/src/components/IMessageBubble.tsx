import clsx from "clsx";
import type { Role } from "../types";

interface Props {
  role: Role;
  text: string;
}

export function IMessageBubble({ role, text }: Props) {
  const isUser = role === "user";
  return (
    <div
      className={clsx(
        "flex w-full mb-0.5",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      <div
        className={clsx(
          "max-w-[70%] px-3.5 py-2 rounded-[18px] text-[15px] leading-snug whitespace-pre-wrap break-words",
          isUser
            ? "bg-imessage-blue text-white"
            : "bg-imessage-grey text-black",
        )}
      >
        {text}
      </div>
    </div>
  );
}
