import { useEffect, useState } from "react";
import type { Persona } from "../types";

interface Props {
  persona: Persona;
  onClose: () => void;
}

export function PersonaReveal({ persona, onClose }: Props) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 20);
    return () => clearTimeout(t);
  }, []);

  const {
    personality,
    demographics,
    summary,
    values_ranked,
    interests,
    dealbreakers,
    conversation_hooks,
  } = persona;

  return (
    <div
      className="absolute inset-0 bg-black/30 flex items-end z-20 transition-opacity duration-300"
      style={{ opacity: mounted ? 1 : 0 }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full bg-white rounded-t-3xl shadow-2xl overflow-y-auto max-h-[85vh] p-6 relative"
        style={{
          transform: mounted ? "translateY(0)" : "translateY(100%)",
          transition: "transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)",
        }}
      >
        <button
          onClick={onClose}
          aria-label="Close"
          className="absolute top-4 right-5 text-gray-400 hover:text-gray-700 text-xl"
        >
          ✕
        </button>

        <div className="text-center mb-6">
          <div className="text-[80px] font-bold tracking-tight text-imessage-blue leading-none">
            {personality.mbti}
          </div>
          <p className="text-[15px] text-gray-600 mt-2 max-w-sm mx-auto">{summary}</p>
        </div>

        <DimensionBars dims={personality.dimensions} />

        <Section title="interests">
          <div className="flex flex-wrap gap-1.5 mt-2">
            {interests.map((i, idx) => (
              <span
                key={idx}
                className={
                  "px-3 py-1 rounded-full text-xs " +
                  (i.depth_signal === "high"
                    ? "bg-imessage-blue text-white"
                    : "bg-imessage-grey text-black")
                }
                title={i.specific_details}
              >
                {i.topic}
              </span>
            ))}
          </div>
        </Section>

        <Section title="top values">
          <ol className="list-decimal list-inside mt-2 space-y-0.5 text-sm">
            {values_ranked.map((v, i) => (
              <li key={i}>{v}</li>
            ))}
          </ol>
        </Section>

        <Section title="instant no">
          <ul className="mt-2 space-y-0.5 text-sm text-red-700">
            {dealbreakers.map((d, i) => (
              <li key={i}>· {d}</li>
            ))}
          </ul>
        </Section>

        <details className="mt-5">
          <summary className="text-xs uppercase tracking-wide text-gray-500 cursor-pointer">
            what a match might open with
          </summary>
          <ul className="mt-2 space-y-1 text-sm text-gray-700">
            {conversation_hooks.map((h, i) => (
              <li key={i}>· {h}</li>
            ))}
          </ul>
        </details>

        <div className="mt-6 text-[10px] text-gray-400">
          {demographics.campus} · {demographics.age} · ~{demographics.travel_radius_km}km radius
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mt-5">
      <div className="text-xs uppercase tracking-wide text-gray-500">{title}</div>
      {children}
    </div>
  );
}

function DimensionBars({ dims }: { dims: Persona["personality"]["dimensions"] }) {
  const rows: Array<{ label: string; left: string; right: string; value: number }> = [
    { label: "Extraversion", left: "I", right: "E", value: dims.extraversion },
    { label: "Intuition", left: "S", right: "N", value: dims.intuition },
    { label: "Thinking", left: "F", right: "T", value: dims.thinking },
    { label: "Judging", left: "P", right: "J", value: dims.judging },
  ];
  return (
    <div className="space-y-3 mt-4">
      <div className="text-[10px] uppercase tracking-wide text-gray-400 text-center">
        continuous dimension scores · mbti letters derived
      </div>
      {rows.map(({ label, left, right, value }) => (
        <div key={label}>
          <div className="flex justify-between text-[11px] mb-0.5">
            <span className="text-gray-600">{label}</span>
            <span className="font-mono text-gray-700">{value.toFixed(2)}</span>
          </div>
          <div className="flex items-center gap-2 text-[11px]">
            <span className="w-3 text-right font-semibold text-gray-500">{left}</span>
            <div className="flex-1 h-1.5 bg-gray-200 rounded-full relative">
              <div
                className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-imessage-blue"
                style={{ left: `calc(${value * 100}% - 6px)` }}
              />
            </div>
            <span className="w-3 text-left font-semibold text-gray-500">{right}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
