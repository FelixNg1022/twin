# Twin — Video Strategy

**Target length:** 4:30–5:00 (spec says ≤5 min)
**Audience:** Ditto AI engineering team evaluating a take-home. Rubric: clean code, infrastructure, product design, customer research, iteration.
**Deliverable:** Unlisted YouTube or Loom link, dropped into submission email + README footer.

---

## Pre-flight checklist (do ALL of this before hitting record)

### Environment
- [ ] Backend running: `cd backend && .venv/bin/uvicorn app.main:app --reload`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] Browser at `http://localhost:5173`, Chrome window sized to **~1440×900** (for the card-on-gray look)
- [ ] Browser zoom at **100%** exactly
- [ ] `ANTHROPIC_API_KEY` real & working (do a test interview end-to-end once, throw away the result)

### Tabs / windows to have open in fixed positions
- **Tab 1 — App:** `http://localhost:5173` (fresh session loaded — *don't* start the interview yet)
- **Tab 2 — Mermaid diagram:** `https://github.com/FelixNg1022/twin/blob/main/docs/state-machine.md` (mermaid renders inline on GitHub)
- **Tab 3 — decisions.md:** `https://github.com/FelixNg1022/twin/blob/main/docs/decisions.md`
- **Tab 4 — README V2 section:** `https://github.com/FelixNg1022/twin#whats-next-v2`
- **VS Code / editor** with these files open and pinned:
  - `backend/app/agent/nodes.py` scrolled to `probe_weekend_node` (~line 200)
  - `backend/app/channels/photon.py`
  - `backend/app/services/structured_call.py`
  - `frontend/src/components/PersonaReveal.tsx` scrolled to `DimensionBars`
- **Terminal 1 (staged for git log beat):**
  ```bash
  cd /Users/felixng/Developer/Twin
  clear
  git log --oneline prompts/probe_weekend.txt
  # then separately:
  git log -p -- backend/prompts/probe_weekend.txt
  ```
- **Terminal 2 (staged for scores-table beat):**
  ```bash
  cd /Users/felixng/Developer/Twin/backend
  clear
  sqlite3 twin.db "SELECT dimension, ROUND(score,2) AS score, evidence FROM scores ORDER BY id;"
  ```

### Recording tool
**Recommended order:**
1. **Screen Studio** (macOS, paid) — best-looking output, automatic smooth zooms on clicks, speed-ramping. Worth the trial if you don't own it.
2. **CleanShot X** — good if you already have it.
3. **OBS Studio** — free, more setup. Works fine.
4. **Loom** — fastest to record+upload but lower polish and auto-trims awkwardly.

### Recording settings
- **Resolution:** 1920×1080 (1080p).
- **Framerate:** 30fps sufficient; 60fps for smoother cursor if your tool supports.
- **Audio:** dedicated mic or AirPods-with-mic. **Do NOT use the Mac built-in mic** — it picks up fan noise and echoes.
- **Mode:** desktop screen only (you can add a face-cam inset but it's optional — voiceover is fine).
- **Quiet room.** Record late at night if you have roommates.

### Dry runs
- Read the full script below out loud **twice** to internalize phrasing.
- Run through the demo interview **once** to check pacing and make sure the reveal fires cleanly.
- Record **one full take** as a rehearsal and watch it. You'll catch pacing issues.
- Then record the real take(s). Most people get it in take 3–4.

---

## The 7 beats

Total: ~5:00. Record each beat **separately** and stitch in editing. If a beat goes sideways, redo just that beat instead of starting over.

### Beat 1 — Cold-open (0:00–0:18, ~18s)

**Visual:** Record your screen during the *last* 3-4 seconds of an actual interview. User types the final dealbreaker, typing indicator says "putting your twin together...", reveal sheet springs up with the giant ISFJ letters + summary.

**Audio:** None. Let the visual breathe. Hard cut to Beat 2.

**Production:**
- Record this at the END of your session (after you've finished an interview for real) — that way the reveal is authentic.
- Trim to 3–4s of actual motion: typing → reveal in → brief hold on ISFJ.
- Optional: subtle audio whoosh on the reveal spring. Most tools have a default sound library.
- This is the hook. The MBTI letters slam-in + summary is the single most visually distinctive moment in the whole project.

### Beat 2 — Why dating + why Twin first (0:18–1:18, ~60s)

**Visual:**
- Start on you on camera (if using face-cam) OR a single clean slide with "The prompt: if you were Ditto's founder, what would you build first?"
- Around 0:35, cut to `docs/research.md` on GitHub scrolled to the top.
- Around 0:55, cut back to app on the reveal card with the MBTI letters — still open from Beat 1.

**Script (~155 words, pace at ~2.5 words/sec):**
> "The prompt: if you're Ditto's founder, what do you build first? Here's the answer that makes sense.
>
> College students hate dating apps because they get commodified into thumbnails — swiping through five hundred strangers hoping one stops scrolling. Ditto's bet flips that: an AI represents you instead, so by the time a human meeting happens, it's already warm.
>
> But that bet only works if the AI has an accurate YOU to represent. Which means the first feature can't be the matcher or the date proposer — it has to be the one that builds the persona. That's Twin.
>
> The design twist — MBTI isn't scientifically rigorous, but college students screenshot their letters and share them. Big Five is what actually predicts relationship outcomes. So Twin probes behavioral questions, scores against all five Big Five factors under the hood, and returns BOTH: an MBTI label users will screenshot, and continuous dimension scores that downstream matching will consume."

**Production:**
- Don't read the research memo line-by-line. Let the viewer glimpse the headline and paragraphs for ~5 seconds while you continue narrating.
- If you cut the length, trim the middle paragraph ("But that bet...") — save the pain-opener and the MBTI-as-culture framing.

### Beat 3 — Live demo (1:18–2:05, ~47s)

**Visual:** Fresh session in the app. Full interview played at natural speed for the interesting moments; demographics sped up 3x.

**Script (~100 words; let silence breathe during the interactions):**
> "Here's the interview end-to-end.
>
> [SPED UP DEMOGRAPHICS — narrate over the speed-ramp]
> Standard demographics — name, age, campus, how far you'd travel for a date. Speeding through that. These questions feel conversational, not like a form.
>
> [PROBE_WEEKEND — natural speed]
> Now the behavioral probes. 'What'd you get up to Saturday night?' I answered with a solo hike. Notice what happens next —
>
> [ADAPTIVE INTEREST BRANCH FIRES]
> — it dug one level deeper on hiking specifically because the model flagged it as distinctive. That's the adaptive branch.
>
> [FAST-FORWARD THROUGH remaining probes, planning, support, stress]
> More probes — trip planning, how I'd support a stressed friend, my own stress. Each one scores a specific Big Five axis.
>
> [REVEAL FIRES]
> And the reveal — MBTI letters up top, continuous dimensions underneath, a summary, conversation hooks a matched partner could open with."

**Production:**
- Use Screen Studio's speed-ramping: 3x on demographics, 1x on probes + reveal.
- Total real interview time is ~2 min; compressed to ~45s through selective speed-up.
- If your app crashes mid-demo, *don't* try to recover on camera. Cut, restart, rerecord.

### Beat 4 — How it's built (2:05–3:35, ~90s)

**Visual:** Multiple cuts — this is the densest beat. 4 sub-beats:

**4a — State machine diagram (~15s)**
- Tab 2 (`docs/state-machine.md` on GitHub). Mermaid renders inline.
> "Under the hood: a LangGraph state machine. Eleven nodes, one conditional branch for the adaptive interest follow-up."

**4b — Merged-call code (~25s)**
- VS Code: `backend/app/agent/nodes.py`, scrolled to `probe_weekend_node`. Cursor/highlight the `structured_call` invocation.
> "Each probe node makes ONE Claude call that returns BOTH the personality score AND the next question in a single structured output. That halves the per-turn latency — and that matters because users are waiting for every message."

**4c — Model routing + channel abstraction (~25s)**
- Quick split screen or two cuts: `backend/app/services/structured_call.py` (pointing at `ANTHROPIC_TURN_MODEL` / `ANTHROPIC_SYNTHESIS_MODEL`) then `backend/app/channels/photon.py`
> "Haiku 4.5 runs every in-turn call. Opus 4.7 runs once at the end for synthesis. Fastest where the user's waiting, smartest where they aren't.
>
> And the Channel abstraction — WebChannel for this demo, PhotonChannel stubbed. Nodes don't know which one they're talking to. Because Ditto delivers over iMessage, not the web — and this separation keeps the agent logic portable to whichever delivery layer ships."

**4d — Big Five / MBTI toggle + scores table (~25s)** — *the showstopper*
- App's reveal card. Click MBTI ⇄ BIG FIVE toggle. Labels swap in place.
- Cut to Terminal 2 (staged). Enter the sqlite command. Shows raw dimension scores with evidence strings.
> "And the scoring model is literally Big Five under the hood — [CLICK BIG FIVE TOGGLE] all five factors including Neuroticism, each from its own dedicated probe. MBTI is a derived wrapper over four of the five axes, not the source of truth.
>
> [CUT TO TERMINAL]
> Every score is evidence-traceable in SQLite — dimension, value, and one-line justification from the LLM. No hand-waving."

**Production notes:**
- The toggle click + label swap is the single best visual beat in the whole video. Make sure the cursor is clearly visible when you click.
- Resize the terminal to a readable font size (14pt+). Clear it before running the command.

### Beat 5 — Decisions / iteration (3:35–4:20, ~45s)

**Visual:** Two sub-beats.

**5a — decisions.md (~15s)**
- Tab 3 on GitHub. Scroll through 5 ADRs briefly.
> "Every non-obvious decision lives in decisions.md — five ADRs. Why we merged the scoring call. Why Haiku for turns, Opus for synthesis. Why the agent halts before each user-input node. Why we threw out LangGraph's built-in checkpointer mid-build when its state-merge semantics broke the demographics transition."

**5b — git log on probe_weekend.txt (~30s)** — *the iteration proof*
- Terminal 1 (staged). Run `git log --oneline prompts/probe_weekend.txt`.
- Show the v1 and v2 commits. Then run `git log -p` to show the diff.
> "And the prompts themselves went through iteration. Here's probe_weekend's git log. [SHOW LOG] V1 asked 'what did you do this past weekend?' Got generic answers. V2 rewrote to 'what'd you get up to Saturday night?' Specific, casual, texture. [SHOW DIFF] One rewrite, significantly better extraction of distinctive interests like the hiking branch you saw earlier."

**Production:**
- This beat is proof that "iteration" in the rubric is more than a claim. The git log is the artifact.
- Make the terminal font big enough to read (16pt+). Use a dark-background terminal theme for contrast on video.

### Beat 6 — V2 roadmap (4:20–4:50, ~30s)

**Visual:** Tab 4 — README scrolled to "What's next (V2)" section.

**Script:**
> "V2 adds the signal no major dating app matches on: humor. Users react to a curated stimulus set, reactions embed into a compatibility vector. Shared humor is ahead of shared hobbies as a predictor of relationship satisfaction in the research.
>
> Two other V2 candidates in the README — a persona-versus-persona simulator that makes Ditto's thousand-dates thesis literal, and a post-date feedback agent that closes the learning loop."

### Beat 7 — Sign-off (4:50–5:05, ~15s)

**Visual:** Either face-cam or the repo page (`github.com/FelixNg1022/twin`).

**Script:**
> "Repo's in the description. Thanks for watching."

Hard stop. Resist the urge to explain more.

---

## Editing checklist

- [ ] Trim dead space at the start and end of every beat
- [ ] ~150ms crossfades between beats (most tools do this with a drag-drop)
- [ ] Add text overlays for key terms as they're spoken: "LangGraph", "Haiku 4.5 / Opus 4.7", "Big Five", "ADR-005" — helps viewers who aren't in the zone
- [ ] Background music: optional, keep it SUBTLE and instrumental. Epidemic Sound / Artlist / YouTube Audio Library. Avoid anything with vocals.
- [ ] Final length check: aim 4:30–5:00. If over 5:00, trim Beat 2 first (the "why" section is the most elastic).
- [ ] Watch the final once at 1x speed with sound on. Once at 1.25x with no sound (catches cursor issues).

---

## Upload & submission

- [ ] Upload to YouTube **Unlisted** (not Private — Ditto needs to watch without login) or Loom with no password
- [ ] Copy the URL
- [ ] Open README.md → replace the `<!-- ![Twin reveal animation](docs/reveal.gif) -->` comment with the video link at the top
- [ ] Alternatively, keep the GIF at top and add a "📹 Walkthrough video: [link]" line underneath
- [ ] Capture the GIF for the README separately — Kap or CleanShot → 3-second loop of the reveal moment → save to `docs/reveal.gif`
- [ ] Commit: `docs: add walkthrough video link + reveal GIF`
- [ ] Submit to Ditto with: (a) video link (b) repo link `github.com/FelixNg1022/twin`

---

## Gotchas

1. **Don't ad-lib explanations mid-recording.** If something goes wrong, CUT, and restart that beat. Ad-libs eat your time budget.
2. **Cursor visibility.** Dark cursors on light backgrounds are hard to see on video. Enable macOS's cursor size bump (System Settings → Accessibility → Display → Pointer size) if recording at desktop resolution.
3. **Notifications.** Enable Do Not Disturb before recording. One Slack ping mid-demo = retake.
4. **Clock visible in menu bar.** Hide system clock (or screenshot in fullscreen mode) — tiny continuity issue on multi-take stitched videos.
5. **Terminal font size.** 14pt minimum, 16pt better. Default 12pt is unreadable at 1080p.
6. **Don't record the first live interview.** Haiku sometimes produces a weird first message. Warm up with one throwaway session before recording.
7. **Capture the reveal GIF while you're already recording.** Don't do two separate recording sessions.

---

## Total prep time

- Pre-flight setup: **15 min**
- Script rehearsal (twice): **15 min**
- Recording (3-4 takes): **45 min**
- Editing: **30 min**
- Upload + README update: **10 min**

**Total: ~2 hours** from cold start to submitted video.

---

## If you're running short on time — minimum-viable video

If you need to cut this to 3 minutes:

1. Drop Beat 2 from 60s → 30s (just the pain→infra pivot, drop the MBTI/Big-Five framing — it surfaces in Beat 4 anyway)
2. Drop Beat 4a (the state-machine diagram) — saves 15s
3. Drop Beat 5a (decisions.md scroll) — saves 15s

Keeps the cold-open, the demo, the merged-call / Haiku-Opus / channel / Big-Five-toggle / scores-table beat (which is the densest signal density in the rubric), the v1→v2 iteration artifact, and V2 roadmap. All the critical evidence, half the length.
