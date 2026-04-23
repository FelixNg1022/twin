import clsx from "clsx";
import type { Role } from "../types";

interface Props {
  role: Role;
  text: string;
  isLastOfRun: boolean;
}

export function IMessageBubble({ role, text, isLastOfRun }: Props) {
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
          // iMessage "tail": last bubble of a run gets a sharpened corner on
          // the sender's side. Full curled tail would need SVG; this reads
          // as the tail-shape at a glance.
          isLastOfRun && isUser && "rounded-br-[6px]",
          isLastOfRun && !isUser && "rounded-bl-[6px]",
        )}
      >
        {text}
      </div>
    </div>
  );
}
