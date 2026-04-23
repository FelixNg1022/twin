import { useEffect, useRef, useState } from "react";
import { ArrowUp } from "lucide-react";

interface Props {
  disabled: boolean;
  onSend: (text: string) => void;
}

export function ComposerBar({ disabled, onSend }: Props) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const wasDisabled = useRef(disabled);
  const canSend = value.trim().length > 0 && !disabled;

  // Refocus whenever the input transitions from disabled → enabled, so the
  // user can keep typing without clicking back into the field after each turn.
  useEffect(() => {
    if (wasDisabled.current && !disabled) {
      inputRef.current?.focus();
    }
    wasDisabled.current = disabled;
  }, [disabled]);

  const submit = () => {
    if (!canSend) return;
    onSend(value.trim());
    setValue("");
    // Keep the input focused during the round-trip; when disabled flips back
    // to false, the effect above is a belt-and-suspenders refocus.
    inputRef.current?.focus();
  };

  return (
    <div className="flex items-end gap-2 px-3 py-2 border-t border-gray-200 bg-white">
      <label htmlFor="composer-input" className="sr-only">
        Message Twin
      </label>
      <input
        ref={inputRef}
        id="composer-input"
        type="text"
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
        className="flex-1 bg-gray-100 rounded-full px-4 py-2 text-[15px] focus:outline-none focus:ring-2 focus:ring-imessage-blue/60 disabled:opacity-60 disabled:cursor-not-allowed"
      />
      <button
        onClick={submit}
        disabled={!canSend}
        aria-label="Send message"
        className="w-11 h-11 rounded-full bg-imessage-blue text-white flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-95 focus:outline-none focus-visible:ring-2 focus-visible:ring-imessage-blue/60 focus-visible:ring-offset-2"
      >
        <ArrowUp size={18} strokeWidth={2.75} />
      </button>
    </div>
  );
}
