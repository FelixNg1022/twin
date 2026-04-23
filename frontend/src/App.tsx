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
    <div className="flex flex-col h-full max-w-[480px] mx-auto bg-white relative sm:my-4 sm:h-[calc(100%-2rem)] sm:rounded-2xl sm:shadow-xl sm:overflow-hidden">
      <button
        onClick={handleReset}
        aria-label="Start over — reset the interview"
        className="absolute top-2 right-2 min-w-11 min-h-11 px-3 text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-100 active:bg-gray-200 rounded-full z-10 focus:outline-none focus-visible:ring-2 focus-visible:ring-imessage-blue/60 focus-visible:ring-offset-2 transition-colors"
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
