import { useEffect, useRef, useState } from "react";
import { ArrowUp } from "lucide-react";

interface Props {
  disabled: boolean;
  onSend: (text: string) => void;
}

const MAX_HEIGHT_PX = 140; // ~6 lines at 15px text

export function ComposerBar({ disabled, onSend }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const wasDisabled = useRef(disabled);
  const canSend = value.trim().length > 0 && !disabled;

  // Auto-resize the textarea to fit content (up to MAX_HEIGHT_PX).
  const resize = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, MAX_HEIGHT_PX)}px`;
  };

  useEffect(() => {
    resize();
  }, [value]);

  // Refocus when input transitions disabled → enabled.
  useEffect(() => {
    if (wasDisabled.current && !disabled) {
      textareaRef.current?.focus();
    }
    wasDisabled.current = disabled;
  }, [disabled]);

  const submit = () => {
    if (!canSend) return;
    onSend(value.trim());
    setValue("");
    textareaRef.current?.focus();
  };

  return (
    <div className="flex items-end gap-2 px-3 py-2 border-t border-gray-200 bg-white">
      <label htmlFor="composer-input" className="sr-only">
        Message Twin
      </label>
      <textarea
        ref={textareaRef}
        id="composer-input"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
        disabled={disabled}
        placeholder="iMessage"
        aria-label="Message Twin"
        autoFocus
        rows={1}
        className="flex-1 resize-none bg-gray-100 rounded-2xl px-4 py-2 text-[15px] leading-snug focus:outline-none focus:ring-2 focus:ring-imessage-blue/60 disabled:opacity-60 disabled:cursor-not-allowed overflow-y-auto"
        style={{ maxHeight: `${MAX_HEIGHT_PX}px` }}
      />
      <button
        onClick={submit}
        disabled={!canSend}
        aria-label="Send message"
        className="w-11 h-11 shrink-0 rounded-full bg-imessage-blue text-white flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-95 focus:outline-none focus-visible:ring-2 focus-visible:ring-imessage-blue/60 focus-visible:ring-offset-2"
      >
        <ArrowUp size={18} strokeWidth={2.75} />
      </button>
    </div>
  );
}
