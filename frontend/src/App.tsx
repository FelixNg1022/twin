import { useState } from "react";
import { useChat } from "./hooks/useChat";

function App() {
  const { messages, isTyping, send } = useChat();
  const [input, setInput] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isTyping) return;
    setInput("");
    await send(text);
  };

  return (
    <div className="flex flex-col h-full max-w-2xl mx-auto p-4">
      <div className="flex-1 overflow-y-auto space-y-2 pb-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-2 rounded ${
              m.role === "user" ? "bg-blue-100 self-end" : "bg-gray-100 self-start"
            }`}
          >
            <strong>{m.role}:</strong> {m.text}
          </div>
        ))}
        {isTyping && <div className="text-gray-400">...</div>}
      </div>
      <form onSubmit={submit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="type a message..."
          disabled={isTyping}
          className="flex-1 border p-2 rounded"
        />
        <button
          type="submit"
          disabled={!input.trim() || isTyping}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default App;
