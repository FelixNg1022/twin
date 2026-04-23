import { useEffect, useRef, useState } from "react";
import { ArrowRight, X } from "lucide-react";
import type { Persona } from "../types";

interface Props {
  persona: Persona;
  onClose: () => void;
}

function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
  );
}

export function PersonaReveal({ persona, onClose }: Props) {
  const [mounted, setMounted] = useState(false);
  const [closing, setClosing] = useState(false);
  const closeBtnRef = useRef<HTMLButtonElement>(null);
  const reducedMotion = useRef(prefersReducedMotion());

  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 20);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    if (mounted && !closing) {
      closeBtnRef.current?.focus();
    }
  }, [mounted, closing]);

  const handleClose = () => {
    if (closing) return;
    setClosing(true);
    const delay = reducedMotion.current ? 0 : 280;
    window.setTimeout(() => onClose(), delay);
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        handleClose();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  const open = mounted && !closing;
  const transitionCss = reducedMotion.current
    ? "none"
    : "transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)";

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="persona-reveal-heading"
      className="absolute inset-0 bg-black/30 flex items-end z-20 transition-opacity duration-300"
      style={{ opacity: open ? 1 : 0 }}
      onClick={handleClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full bg-white rounded-t-3xl shadow-2xl overflow-y-auto max-h-[85vh] p-6 relative"
        style={{
          transform: open ? "translateY(0)" : "translateY(100%)",
          transition: transitionCss,
        }}
      >
        <button
          ref={closeBtnRef}
          onClick={handleClose}
          aria-label="Close"
          className="absolute top-3 right-3 w-11 h-11 flex items-center justify-center rounded-full text-gray-500 hover:text-gray-800 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-imessage-blue focus-visible:ring-offset-2"
        >
          <X size={20} strokeWidth={2.25} />
        </button>

        <div className="text-center mb-6">
          <h1
            id="persona-reveal-heading"
            className="text-[80px] font-bold tracking-tight text-imessage-blue leading-none"
          >
            {personality.mbti}
          </h1>
          <p className="text-[15px] text-gray-700 mt-2 max-w-sm mx-auto leading-snug">
            {summary}
          </p>
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
                    ? "bg-imessage-blue text-white font-semibold ring-2 ring-imessage-blue/20"
                    : "bg-imessage-grey text-black font-normal")
                }
                title={i.specific_details || i.topic}
                aria-label={
                  i.depth_signal === "high"
                    ? `${i.topic} (high depth — ${i.specific_details || "details on file"})`
                    : `${i.topic} (${i.depth_signal} depth)`
                }
              >
                {i.depth_signal === "high" ? "★ " : ""}
                {i.topic}
              </span>
            ))}
          </div>
        </Section>

        <Section title="top values">
          <ol className="list-decimal list-inside mt-2 space-y-0.5 text-sm text-gray-800">
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

        <details className="mt-5 group">
          <summary className="text-xs uppercase tracking-wide text-gray-600 cursor-pointer inline-flex items-center gap-1 py-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-imessage-blue focus-visible:ring-offset-2 rounded">
            <ArrowRight
              size={12}
              className="transition-transform group-open:rotate-90"
            />
            what a match might open with
          </summary>
          <ul className="mt-2 space-y-1 text-sm text-gray-800">
            {conversation_hooks.map((h, i) => (
              <li key={i}>· {h}</li>
            ))}
          </ul>
        </details>

        <div className="mt-6 text-[11px] text-gray-500">
          {demographics.campus} · {demographics.age} · ~{demographics.travel_radius_km}km radius
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mt-5">
      <h2 className="text-xs uppercase tracking-wide text-gray-600 font-semibold">
        {title}
      </h2>
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
      <div className="text-[10px] uppercase tracking-wide text-gray-500 text-center">
        continuous dimension scores · mbti letters derived
      </div>
      {rows.map(({ label, left, right, value }) => {
        const dominantLetter = value >= 0.5 ? right : left;
        return (
          <div key={label}>
            <div className="flex justify-between text-[11px] mb-0.5">
              <span className="text-gray-700">{label}</span>
              <span className="font-mono text-gray-800">{value.toFixed(2)}</span>
            </div>
            <div className="flex items-center gap-2 text-[11px]">
              <span className="w-3 text-right font-semibold text-gray-600">{left}</span>
              <div
                role="meter"
                aria-label={`${label}: ${value.toFixed(2)}, skewing toward ${dominantLetter}`}
                aria-valuenow={Number(value.toFixed(2))}
                aria-valuemin={0}
                aria-valuemax={1}
                className="flex-1 h-1.5 bg-gray-200 rounded-full relative"
              >
                <div
                  className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-imessage-blue"
                  style={{ left: `calc(${value * 100}% - 6px)` }}
                />
              </div>
              <span className="w-3 text-left font-semibold text-gray-600">{right}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
