import { useState } from "react";
import { useChat } from "./hooks/useChat";
import { ChatWindow } from "./components/ChatWindow";
import { ComposerBar } from "./components/ComposerBar";
import { PersonaReveal } from "./components/PersonaReveal";

function App() {
  const { messages, isTyping, complete, persona, send, reset } = useChat();
  const [revealDismissed, setRevealDismissed] = useState(false);

  const typingLabel =
    isTyping && messages.length > 12
      ? "putting your twin together..."
      : undefined;

  const handleReset = async () => {
    setRevealDismissed(false);
    await reset();
  };

  return (
    <div className="flex flex-col h-full max-w-[480px] mx-auto bg-white relative">
      <button
        onClick={handleReset}
        className="absolute top-2 right-3 text-xs text-gray-400 hover:text-gray-700 z-10"
      >
        Start over
      </button>
      <ChatWindow
        messages={messages}
        isTyping={isTyping}
        typingLabel={typingLabel}
      />
      <ComposerBar disabled={isTyping} onSend={send} />
      {complete && persona && !revealDismissed && (
        <PersonaReveal
          persona={persona}
          onClose={() => setRevealDismissed(true)}
        />
      )}
    </div>
  );
}

export default App;
