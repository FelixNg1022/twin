export function TypingIndicator({ label }: { label?: string }) {
  return (
    <div className="flex justify-start mb-0.5">
      <div className="bg-imessage-grey rounded-[18px] px-4 py-2.5 flex items-center gap-1">
        <Dot delay={0} />
        <Dot delay={150} />
        <Dot delay={300} />
        {label && (
          <span className="ml-2 text-[13px] text-gray-600">{label}</span>
        )}
      </div>
    </div>
  );
}

function Dot({ delay }: { delay: number }) {
  return (
    <span
      className="inline-block w-1.5 h-1.5 rounded-full bg-gray-500 animate-[pulse_1s_ease-in-out_infinite]"
      style={{ animationDelay: `${delay}ms` }}
    />
  );
}
