import { useState } from "react";

interface Props {
  disabled: boolean;
  onSend: (text: string) => void;
}

export function ComposerBar({ disabled, onSend }: Props) {
  const [value, setValue] = useState("");
  const canSend = value.trim().length > 0 && !disabled;

  const submit = () => {
    if (!canSend) return;
    onSend(value.trim());
    setValue("");
  };

  return (
    <div className="flex items-end gap-2 px-3 py-2 border-t border-gray-200 bg-white">
      <input
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
        className="flex-1 bg-gray-100 rounded-full px-4 py-2 text-[15px] outline-none disabled:opacity-60"
      />
      <button
        onClick={submit}
        disabled={!canSend}
        aria-label="Send"
        className="w-8 h-8 rounded-full bg-imessage-blue text-white flex items-center justify-center disabled:opacity-30 transition-opacity"
      >
        ↑
      </button>
    </div>
  );
}
