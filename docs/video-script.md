# Twin — Video Script & Shot List

Paced at ~130 words/min (slower, measured). Total ~4:35. Keep this on a second screen while recording.

For prep checklist, gear, tools, and editing advice, see [video-plan.md](video-plan.md).

---

## 🎬 Beat 1 — Cold-open (0:00 → 0:15, 15s)

**Need:** 3–4 seconds of real screen footage — the last turn of an interview, recorded at the END of your session. Dealbreaker answer → typing indicator → reveal card springs up with ISFJ letters.

**See:** Reveal spring, ISFJ visible for ~1s, hard cut.

**Say:** (nothing — visual only, let it breathe)

---

## 🎬 Beat 2 — Why Twin first (0:15 → 1:05, 50s)

**Need:**
- Tab on `docs/research.md` at the top on GitHub
- Optional face-cam

**See:**
- 0:15–0:30 → face-cam or title card "If you're Ditto's founder, what do you build first?"
- 0:30–0:50 → research.md, scroll slowly through Problem + MBTI+BigFive sections
- 0:50–1:05 → back to app reveal card from Beat 1

**Say:** (~115 words)

> The prompt is: **if you're Ditto's founder, what do you build first?**
>
> *(pause)*
>
> Here's the thing about dating apps. Students get commodified into thumbnails. Swiping through five hundred strangers. Hoping one stops scrolling.
>
> Ditto flips that. An AI represents you. So the human meeting is already warm.
>
> *(pause)*
>
> But that only works if the AI has an accurate *you* to represent. Which means the first feature can't be the matcher. Or the date proposer. It has to be the one that **builds the persona.**
>
> That's Twin.
>
> *(pause)*
>
> The twist — MBTI isn't scientifically rigorous. But college students screenshot their letters and share them. So Twin scores all five **Big Five** factors under the hood. And shows MBTI on the surface.

---

## 🎬 Beat 3 — Live demo (1:05 → 1:50, 45s)

**Need:**
- Fresh app session at 1440×900
- Screen Studio speed-ramping (3× demographics, 1× probes + reveal)
- Pre-rehearsed answers

**Answers to type (memorize these):**
1. `alex` → `20` → `female` → `straight` → `uc berkeley` → `30km`
2. Weekend: `went on a solo hike saturday, then read for a few hours`
3. Hiking follow-up: `mt tam mostly, did the west coast trail last summer`
4. Planning: `i make a spreadsheet with everything booked two weeks out`
5. Support: `i'd just sit with them and let them talk`
6. Stress: `got stressed before my stats midterm, didn't sleep well for 2 nights but slept it off`
7. Values: `growth, stability, adventure`
8. Dealbreakers: `smokers, doesn't want kids`

**See:** Greeting → demographics (3×) → probes at 1× → reveal spring.

**Say:** (~60 words with silences)

> Here's the interview end-to-end.
>
> *(let sped-up demographics play silently)*
>
> Name, age, campus, travel radius. Speeding through.
>
> *(slow back to real-time on probe_weekend)*
>
> Now the behavioral probes. *"What'd you get up to Saturday night?"* I answer with a solo hike.
>
> *(adaptive branch fires — pause on the follow-up question)*
>
> Notice that. It just went one level deeper on the hike. Because the model flagged it as distinctive.
>
> *(fast-forward remaining probes, narrate over)*
>
> More probes. Trip planning. Supporting a stressed friend. Then your own stress.
>
> *(reveal fires)*
>
> And the reveal.

---

## 🎬 Beat 4 — How it's built (1:50 → 3:20, 90s) ⭐

Record as 4 sub-cuts and stitch.

### 4a — State machine (1:50 → 2:05, 15s)

**Need:** Tab on `docs/state-machine.md` on GitHub (mermaid renders inline).

**Say:** (~30 words)

> Under the hood. A **LangGraph state machine.** Eleven nodes. One conditional branch — for the adaptive interest follow-up you just saw.

### 4b — Merged call (2:05 → 2:30, 25s)

**Need:** VS Code on `backend/app/agent/nodes.py`, scrolled to `probe_weekend_node` (~line 200). Cursor hovering over `structured_call(...)`.

**Say:** (~50 words)

> Each probe node makes **one** Claude call. It returns the score. And the next question. In a single structured output.
>
> *(pause)*
>
> That halves per-turn latency. Which matters — because users are waiting for every message.

### 4c — Model routing + Channel (2:30 → 2:55, 25s)

**Need:**
- `backend/.env.example` showing `ANTHROPIC_TURN_MODEL` + `ANTHROPIC_SYNTHESIS_MODEL`
- `backend/app/channels/photon.py`

**Say:** (~55 words)

> Haiku four-point-five runs every in-turn call. Opus four-point-seven runs once at synthesis. Fastest where the user's waiting. Smartest where they aren't.
>
> *(cut to photon.py)*
>
> And the **Channel abstraction**. WebChannel for this demo. PhotonChannel stubbed. Nodes don't know which one they're talking to. Because Ditto delivers over iMessage — not the web.

### 4d — Big Five toggle + scores table (2:55 → 3:20, 25s) ⭐⭐

**Need:**
- App open on reveal card from Beat 3 (still visible)
- Terminal staged with:
  ```bash
  sqlite3 twin.db "SELECT dimension, ROUND(score,2) AS score, evidence FROM scores ORDER BY id;"
  ```

**See:**
- Hover over MBTI ⇄ BIG FIVE toggle
- Click **BIG FIVE** — labels swap, Neuroticism appears as 5th row
- Cut to terminal, hit enter

**Say:** (~55 words)

> And the scoring. It's literally **Big Five** under the hood.
>
> *(click the Big Five toggle — pause on the label swap)*
>
> All five factors. Including Neuroticism, from its own probe. MBTI is just the derived wrapper.
>
> *(cut to terminal, hit enter)*
>
> Every score is evidence-traceable in SQLite. Dimension. Value. One-line justification from the model. No hand-waving.

---

## 🎬 Beat 5 — Decisions & iteration (3:20 → 4:00, 40s)

**Need:**
- Tab on `docs/decisions.md` on GitHub
- Terminal with these pre-typed:
  ```bash
  git log --oneline backend/prompts/probe_weekend.txt
  git log -p backend/prompts/probe_weekend.txt
  ```

**See:**
- 3:20–3:30 → decisions.md, scroll through 5 ADRs
- 3:30–4:00 → terminal. First command → v1 + v2 commit hashes. Second command → the diff.

**Say:** (~85 words)

> Every non-obvious decision is in **decisions.md.** Five ADRs.
>
> *(scroll slowly)*
>
> Why we merged the scoring call. Why Haiku for turns, Opus for synthesis. Why we threw out LangGraph's built-in checkpointer mid-build when its state-merge semantics broke.
>
> *(cut to terminal, run git log)*
>
> And the prompts went through iteration. Here's probe_weekend.
>
> *(pause on log)*
>
> V1 asked *"what did you do this past weekend?"* Formal. Generic answers.
>
> V2 rewrote to *"what'd you get up to Saturday night?"* Specific. Casual. Way better extraction.

---

## 🎬 Beat 6 — V2 roadmap (4:00 → 4:25, 25s)

**Need:** README scrolled to "What's next (V2)" section.

**See:** Humor signal paragraph visible, brief mention of simulator + feedback agent.

**Say:** (~55 words)

> V2 adds the signal **no major dating app matches on.** Humor.
>
> Users react to a curated stimulus set. Reactions embed into a compatibility vector. Research puts shared humor **ahead of shared hobbies** as a predictor.
>
> Two more in the roadmap. A persona-versus-persona simulator. And a post-date feedback agent that closes the learning loop.

---

## 🎬 Beat 7 — Sign-off (4:25 → 4:35, 10s)

**Need:** Face-cam OR repo homepage on screen.

**Say:**

> Repo's in the description. Thanks for watching.

Hard stop.

---

## Total 4:35 (25s under the 5:00 cap)

If you're running long, trim Beat 2 first (drop the middle paragraph). If short, you're rushing Beat 2 or Beat 4 — slow down.

## Pacing reminders for slow delivery

- **One sentence at a time.** Complete the thought, then pause before the next.
- **Breath points** marked `(pause)` are deliberate 0.5–1s silences. They sound confident, not rushed.
- Don't blur clauses together — "under the hood / a LangGraph state machine / eleven nodes" as three distinct beats, not one continuous sentence.
- When switching visuals (cuts), stop talking briefly so the edit has a natural pause to hide in.
- Read the script out loud twice before recording. You'll find your own natural phrasing — don't read word-for-word on camera.
