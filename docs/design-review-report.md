# Design Review — Twin frontend

*Applied OneRedOak's design-review workflow (Phases 0–7). Live testing via chrome-devtools MCP against http://localhost:5173. Viewports tested: 1440×900, 768×1024, 375×812.*

*Screenshots in `docs/design-review-screenshots/`.*

---

## Summary

The product delivers its core design intent cleanly: iMessage-authentic styling, a cold-open-worthy persona reveal with a legible spring animation, and a mobile viewport that genuinely passes for iMessage. Accessibility passes on the basics (Tab order is sensible, Esc closes the modal, focus rings are visible, dimension bars are `role="meter"`, no console errors across the full flow). Composer focus-keeping works — typing flow is uninterrupted across turns.

The remaining issues are almost all about **desktop presentation at wide viewports**. The 480px centered chat column is correct for mobile, but on a 1440px screen it reads as a tiny sliver in an ocean of white. For a walkthrough video recorded at desktop resolution, this is the most visible issue.

---

## Findings

### Blockers

None. No functional or accessibility failures blocking merge.

### High-Priority

**1. Empty whitespace on desktop viewports.** At 1440×900, the 480px-max chat column is centered with ~480px of dead white space on each side. No backdrop, no device frame, no secondary content — reads as a half-designed page. This is the most visible issue in the walkthrough video cold-open.
*Evidence: `07-desktop-empty-space.png`.*

**2. Single-line composer (vs. iMessage multi-line textarea).** A 160-character message renders as a single line with horizontal scroll instead of wrapping/growing vertically. Real iMessage uses a growing `<textarea>`. Rare but noticeable when users write longer answers (adaptive-interest probes about hiking, etc.).
*Evidence: `08-long-input.png`.*

### Medium-Priority

**3. No visual frame separates the chat area from the page.** Relates to #1 but distinct: iMessage on macOS shows the chat as a white card against a gray desktop. A subtle body background (e.g. `#f2f2f7` iOS-native gray) would make the 480px column read as a focused window rather than a centered strip.

**4. Reveal modal backdrop dim is subtle.** `bg-black/30` is visible but Material Design recommends 40–60% for scrim opacity. At 1440px with lots of white surrounding the reveal, the modal doesn't strongly pop off the background.
*Evidence: `03-desktop-reveal.png`.*

**5. No loading placeholder before the first greeting.** On page load, the chat is empty until the Anthropic call returns (~500–800ms with Haiku). A subtle skeleton bubble or a pre-rendered "…" would prevent the flash of empty chat.

**6. "Start over" button visually detached at wide viewports.** Positioned at the top-right of the 480px column, it floats alone ~720px away from any content anchor on a 1440px viewport. Works fine on mobile and tablet; mildly awkward on desktop.

### Nitpicks

- **Nit:** Agent bubbles wrap with short first line / wider continuation on some messages because `max-w-[70%]` hits around 340px. Acceptable iMessage behavior — flagging for awareness, not fix.
- **Nit:** Reveal card summary is `text-gray-700` which is slightly soft against the big blue ISFJ header. Could go `text-gray-800` or `text-black` for stronger hierarchy.
- **Nit:** `UC Berkeley · 20 · ~30km radius` metadata at reveal-card bottom is 11px — tiny but acceptable for secondary info.
- **Nit:** No "Delivered" indicator under last outbound bubble (spec Tier 3 optional — correctly deferred).

---

## Code-level fix plan (for the top 3 issues)

**Fix #1, #3, #6 together** — set a soft body background so the 480px column becomes a card:

```css
/* frontend/src/index.css */
body {
  background: #f2f2f7; /* iOS system gray */
}
```

And on the App wrapper:
```tsx
<div className="flex flex-col h-full max-w-[480px] mx-auto bg-white relative shadow-xl md:my-4 md:rounded-2xl md:h-[calc(100%-2rem)] md:overflow-hidden">
```

This gives you a white chat card floating on a gray desktop backdrop with soft shadow + rounded corners on tablet/desktop, while remaining full-bleed on mobile.

**Fix #2** — swap `<input>` → auto-growing `<textarea>` in `ComposerBar`:
Use `rows={1}` and dynamically adjust `rows` or `height` based on scrollHeight. ~10 lines.

**Fix #4** — backdrop `bg-black/30` → `bg-black/50` in `PersonaReveal`. 1-char change.

**Fix #5** — show a `TypingIndicator` placeholder in the chat on initial mount before the first message arrives. ~3 lines in `useChat`.

---

## What's confirmed working well

- ✅ **Keyboard navigation** — Tab order is `Start over → composer → (send when enabled)`; Enter submits; Esc closes modal; focus returns to close button when modal opens
- ✅ **No console errors or warnings** across the full 12-turn flow
- ✅ **Mobile viewport (375px)** passes visual inspection — the chat reads as authentic iMessage; reveal card adapts cleanly
- ✅ **Composer auto-refocus** after each turn works; typing flow uninterrupted
- ✅ **High-depth interest chip** has color + bold + ring + ★ glyph (not color-only per WCAG color-not-only rule)
- ✅ **Reveal spring animation** lands in ~500ms with cubic-bezier overshoot — video-ready cold-open
- ✅ **Focus rings visible** on all interactive controls
- ✅ **Dimension bars** have `role="meter"` + `aria-valuenow`/`min`/`max` + descriptive `aria-label`
- ✅ **Modal semantics** correct: `role="dialog"`, `aria-modal="true"`, `aria-labelledby="persona-reveal-heading"`, `prefers-reduced-motion` respected
