---
title: Twin — Design Spec
date: 2026-04-22
status: Approved — ready for implementation plan
audience: Ditto AI take-home challenge
---

# Twin — Design Spec

> An onboarding agent that creates your digital double for Ditto's matchmaking engine.

## Context

Ditto AI is an iMessage-based matchmaker for college students. No swiping, no
profiles, no in-app chat — users text an AI agent their preferences, the agent
builds a persona, the backend simulates matches, and one date is proposed per
week.

This take-home answers the prompt *"You're a founder of a modern dating
platform — how would you approach building the first version and what feature
would you create first?"* The deliverable is a working feature and a ≤5-minute
walkthrough video. Evaluation criteria: clean code, infrastructure, product
design, customer research, iteration.

**Realistic build budget:** ~6–8 hours of active work, not the 90–120 min Ditto
cites. The user has explicitly opted out of the stated cap to land a video-
worthy artifact.

---

## 1. Feature choice & founder narrative

### Why Twin is the right first feature

Ditto's thesis — *"your AI persona dates 1000 times in simulation before humans
meet"* — has three infrastructure layers: (1) the persona, (2) the match
simulator, (3) the human-facing date proposer. Without layer 1, the other two
are inert. The first feature has to either *be* the persona or produce one as
a byproduct. **Twin** — the onboarding interview that creates it — is the
architectural first move.

It's also the only layer that's demonstrable with a single user. The simulator
needs 2+ personas; the date proposer needs a match graph. Twin works solo.

### Three design choices that make Twin feel Ditto-native

1. **MBTI as culture signal, Big Five as ground truth.** MBTI isn't
   scientifically rigorous, but college students self-identify with it and
   share it socially. Big Five predicts relationship outcomes (Finkel &
   Eastwick meta-analyses — verify exact claim when writing `research.md`).
   Twin probes on Big Five-adjacent behavioral dimensions under the hood,
   returns both: continuous dimension scores *and* an MBTI label the user will
   screenshot and send to friends.
2. **Never ask direct personality questions.** Self-report is noisy. "A friend
   just went through a breakup — what do you say first?" reveals T/F through
   behavior. Biggest single quality lever in the whole design.
3. **iMessage styling isn't decoration — it's the delivery channel.** Ditto
   lives in iMessage; onboarding that doesn't look like iMessage is off-brand
   on day one. The `Channel` abstraction (with a stubbed `PhotonChannel`)
   signals understanding that Ditto is decoupling agent logic from delivery.

### 5-minute video outline (the artifact being graded)

| # | Beat | Time | Purpose |
|---|------|------|---------|
| 1 | **Cold-open** | ~20s | Persona reveal moment, no voiceover intro. Visual hook. |
| 2 | **Why dating + why Twin first** | ~60s | Pain → infra pivot (see below), then the MBTI/Big-Five design choice |
| 3 | **Full demo** | ~45s | Fresh session, fast-forward middle turns, land on reveal |
| 4 | **How it's built** | ~90s | LangGraph diagram, merged-call code pull, Haiku/Opus split, channel abstraction |
| 5 | **Decisions / iteration** | ~45s | `decisions.md` on screen, 2 rev1→rev2 beats, `git log prompts/` |
| 6 | **V2 roadmap** | ~30s | Humor signal headline; simulator + feedback agent as runners-up |
| 7 | **Sign-off** | ~15s | "Repo's here, thanks." |

Total: 5:05 — just under the 5-min soft cap.

### Lead narrative — pain → infra pivot

Opening 20–25 seconds:

> "College students hate swiping because it commodifies them — you're a
> thumbnail competing against 500 other thumbnails. Ditto's bet is that AI
> represents you instead, so the human meeting is warm by default. But
> AI-as-representation only works if the AI has an accurate *you* to
> represent. So the first feature has to be the thing that creates that
> representation. That's Twin."

One paragraph earns points on *customer research* (pain), *product design*
(why Ditto's model solves it), and *feature choice* (why this one first).

---

## 2. Architecture

### Stack

- **Backend:** FastAPI + uvicorn, Python 3.11+
- **Agent:** LangGraph (state machine + mermaid export)
- **LLM:** Anthropic SDK
  - `claude-haiku-4-5-20251001` for all in-turn calls
  - `claude-opus-4-7` for the `synthesize` call only
  - `claude-sonnet-4-6` as a documented fallback for probes (not pre-built —
    activate only if Haiku feels sterile in testing)
- **Persistence:** SQLite via SQLAlchemy
- **Frontend:** Vite + React 19 + TypeScript + Tailwind v3, plain HTTP (no
  websockets)

### Environment variables (`.env.example`)

```text
ANTHROPIC_API_KEY=
ANTHROPIC_TURN_MODEL=claude-haiku-4-5-20251001
ANTHROPIC_SYNTHESIS_MODEL=claude-opus-4-7
DATABASE_URL=sqlite:///./twin.db
CORS_ORIGINS=http://localhost:5173
```

Splitting the model into `TURN_MODEL` + `SYNTHESIS_MODEL` env vars means the
Haiku→Sonnet fallback (ADR-002) is a one-line config change, not a code
change. Also makes the model-routing story legible from `.env.example` alone.

### State graph

10 nodes, one conditional edge:

```
greeting → demographics → probe_weekend → [conditional] → probe_planning
                                                ↓ (if interest_to_probe is set)
                                          adaptive_interest → probe_planning
probe_planning → probe_support → values_rank → dealbreakers → synthesize → reveal
```

Node → dimension mapping:

- `greeting`, `demographics`, `values_rank`, `dealbreakers`, `adaptive_interest`, `reveal` — no personality scoring
- `probe_weekend` → `extraversion` (also fires interest-mining)
- `probe_planning` → `intuition` + `judging` (two dimensions from one response)
- `probe_support` → `thinking`
- `synthesize` → Opus one-shot that produces final `Persona`

### Merged scoring + next-question call

Each probe node makes **one** Claude call that returns structured output:

```python
class ProbeOutput(BaseModel):
    scores: dict[str, float]           # e.g. {"intuition": 0.7, "judging": 0.4}
    evidence: str                      # 1-line justification
    interests_detected: list[str]      # topics mentioned
    interest_to_probe: str | None      # used only by probe_weekend
    next_message: str                  # iMessage-texture reply
```

Adaptive probe uses a smaller schema (no scoring):

```python
class InterestProbeOutput(BaseModel):
    specific_details: str
    depth_signal: Literal["low", "medium", "high"]
    next_message: str
```

Rationale: originally spec had scoring + next-question as two sequential calls.
Merging halves per-turn latency and co-locates scoring rubric with question
generation in the prompt — changing one forces consideration of the other.

### Model routing rule

**Fastest model where the user is waiting, smartest where they aren't.**

- Haiku for every in-turn call (~500–800ms) — iMessage-feel latency
- Opus for `synthesize` (~10–15s) — runs under *"putting your twin together..."*
  typing indicator, where users expect a beat before the reveal

### Channel abstraction

```python
class Channel(ABC):
    async def deliver(self, session_id: str, text: str) -> None: ...

class WebChannel(Channel):
    """Buffers outbound messages into the current HTTP response."""
    async def deliver(self, session_id: str, text: str) -> None: ...

class PhotonChannel(Channel):
    """Stub. Real implementation would call Photon Spectrum SDK.
    Not wired for this demo — see Photon docs."""
    async def deliver(self, session_id: str, text: str) -> None:
        raise NotImplementedError("Photon delivery not configured")
```

Node functions receive `channel` as an argument (not stored in state) and call
`channel.deliver(...)` — unaware of whether they're talking to a browser or
Photon. Inbound messages are handled by the FastAPI route, not by `Channel`
(web is request/response; real Photon would use a webhook handler that also
doesn't belong in `Channel`).

### API surface

```text
POST /sessions
  Request:  (empty body)
  Response: 201 {session_id: str, agent_messages: list[str]}

POST /sessions/{id}/messages
  Request:  {text: str}
  Response: 200 {agent_messages: list[str], complete: bool}

GET /sessions/{id}/persona
  Response: 200 Persona            (if session.complete == true)
            409 {error: "..."}     (if session not yet complete)
            404                    (if session_id unknown)
```

On `complete: true`, the frontend calls `GET /sessions/{id}/persona` to fetch
the structured Persona for the reveal card. The messages endpoint stays lean
(no embedded persona) so the two concerns don't leak into each other.

**Turn-completion semantics:** the message handler runs `graph.astream()`
until the graph halts at a node that requires user input or sets
`complete: true`. `WebChannel` buffers outbound calls into a list during the
run; the handler returns the buffered list. Each HTTP request = one or more
agent replies then a wait for user input.

### Persistence

Three SQLite tables:

```
sessions        (id, created_at, complete, persona_json TEXT)
messages        (id, session_id FK, role, text, created_at)
scores          (id, session_id FK, dimension, score, evidence, probe_node, created_at)
```

The `scores` table is deliberately separate (not JSON-stuffed) so
`sqlite3 twin.db "select * from scores"` becomes a one-command video beat
demonstrating score traceability.

---

## 3. Data model

### Persona (final output schema)

```python
class Persona(BaseModel):
    session_id: str
    summary: str                       # 1-sentence warm description, headline for reveal card
    demographics: Demographics
    personality: Personality
    values_ranked: list[str]           # top 3 from {ambition, family, adventure, growth, stability, creativity}
    interests: list[Interest]
    dealbreakers: list[str]
    conversation_hooks: list[str]      # 3 specific openers a matched partner could use
    created_at: datetime

class Demographics(BaseModel):
    age: int
    gender: str
    sexual_orientation: str
    campus: str
    travel_radius_km: int

class Personality(BaseModel):
    mbti: str                          # derived from dimensions
    dimensions: PersonalityDimensions

class PersonalityDimensions(BaseModel):
    extraversion: float                # avg across probes that scored this dimension
    intuition: float
    thinking: float
    judging: float

class Interest(BaseModel):
    topic: str
    depth_signal: Literal["low", "medium", "high"]
    specific_details: str              # empty string if depth is "low"
```

The `summary` and `conversation_hooks` fields are generated by the `synthesize`
Opus call from the full transcript — they're the sneakiest-good part of the
persona (turn onboarding output into downstream matching fuel).

### Depth signal assignment (synthesize prompt rule)

- `high` — the interest that went through `adaptive_interest` (has real
  `specific_details`)
- `medium` — mentioned with a concrete detail but no follow-up probe
- `low` — mentioned once in passing, no detail

### Message (shared by AgentState and the `messages` DB table)

```python
class Message(BaseModel):
    role: Literal["user", "assistant"]
    text: str
    created_at: datetime
```

### AgentState (in-flight, LangGraph state)

```python
class AgentState(BaseModel):
    session_id: str
    messages: list[Message]
    current_node: str                                # initial value: "greeting"
    first_name: str | None = None                   # captured by the greeting node, used by synthesize for summary
    demographics: Demographics | None = None
    dimension_scores: dict[str, list[float]] = {}   # {"extraversion": [0.7], "intuition": [0.3, 0.8], ...}
    interests_detected: list[str] = []              # topic names accumulated across probes
    interest_probed: Interest | None = None         # the one that went through adaptive_interest
    values_ranked: list[str] = []
    dealbreakers: list[str] = []
    complete: bool = False
```

`channel` is NOT a field on AgentState — it's passed as an argument to node
functions by the graph runner. Keeps state Pydantic-serializable and avoids
leaking delivery layer into domain state. Mutable default fields (`dict`, `list`)
use Pydantic v2 `Field(default_factory=...)` in the actual implementation —
shown as literal defaults here for readability.

### MBTI derivation

For each of `{extraversion, intuition, thinking, judging}`:
- If at least one score exists: `avg(scores) >= 0.5` → first letter (E/N/T/J),
  else second letter (I/S/F/P)
- If zero scores exist (e.g., probe_support was cut per cut-line): default to
  `0.5` → resolves to second letter (I/S/F/P)

Document any unmeasured dimension in the `decisions.md` ADR for the cut.

---

## 4. Frontend

### Tier 1 — Must-have (the video doesn't work without these)

1. **iMessage bubble system**
   - Blue outbound: `#007aff` bg, white text, right-aligned, `rounded-[18px]`
   - Grey inbound: `#e5e5ea` bg, black text, left-aligned, `rounded-[18px]`
   - Font stack: `-apple-system, "SF Pro Display", system-ui, sans-serif`
   - No app chrome (no header, no sidebar) — full-bleed chat, composer pinned bottom
2. **Typing indicator** — grey inbound bubble, 3 animated dots, staggered
   opacity pulse. Appears during every LLM call. During the long Opus
   synthesize, copy changes to *"putting your twin together..."* for flavor.
3. **Composer bar** — rounded pill input, blue circular send button, enabled
   only when text exists. Enter key sends. **Composer locks while agent is
   responding** (typing indicator visible = composer disabled) to prevent
   concurrent requests.
4. **Persona reveal bottom sheet** — slides up from bottom when `complete: true`.
   Covers ~80% of viewport, dims chat behind, close button top-right.
   Spring animation using `cubic-bezier(0.34, 1.56, 0.64, 1)` overshoot on
   slide-in — **this specific animation is the cold-open frame of the video,
   not optional polish.**
   - Big MBTI letters (~120pt, centered)
   - Summary sentence, 16pt grey
   - 4 dimension bars with `I ← ● → E` style labels
   - Interest chips, `high`-depth highlighted
   - Top 3 values as ranked list
   - Dealbreakers as muted-red section
   - Conversation hooks collapsed under a disclosure
5. **Auto-scroll** on new message (smooth); don't yank user back if scrolled up
6. ***Start over* link** — small floating top-corner reset, 10 lines of code,
   useful for demo recording retakes

### Tier 2 — Should-have (~20 min total)

1. **Bubble tail** on last bubble of consecutive sender's run (the curl)
2. **Timestamp separators** between gaps > 1 min (centered grey text)

### Tier 3 — Nice-to-have (cut first)

1. *"Delivered"* text under last outbound bubble
2. Haptic-style bounce on reveal card

### Component tree

```
src/
├── App.tsx                    # session bootstrap, top-level state
├── hooks/
│   └── useChat.ts             # { messages, sendMessage, isTyping, persona, complete }
├── components/
│   ├── ChatWindow.tsx         # scrollable message list, auto-scroll
│   ├── IMessageBubble.tsx     # single bubble with variant + tail flag
│   ├── TypingIndicator.tsx    # 3-dot animated inbound bubble
│   ├── ComposerBar.tsx        # pinned input + send
│   └── PersonaReveal.tsx      # bottom-sheet card
└── types.ts                   # mirrors backend Pydantic schemas
```

`useChat` is the API boundary — dumb components above, HTTP calls inside. One
file to open in the video code walkthrough.

---

## 5. Rubric-aligned artifacts

These artifacts exist to be visible in the video. Their *content* must be real —
manufactured iteration looks worse than no iteration.

### `docs/research.md` (~400-500 words)

Sections:
- **Problem** — college dating UX pain (swipe commodification, message
  fatigue, low match→date conversion). 2-3 sources: Pew 2023 dating survey,
  Ditto founder press quotes, 1 pain thread.
- **Why self-report fails for personality** — cite Finkel & Eastwick (2017)
  meta-analysis claim (verify before writing). Demographic + self-reported-
  preference models predict outcomes near chance; behavioral signals do better.
- **Why MBTI + Big Five together** — MBTI cultural footprint vs. Big Five
  validation.
- **Design implications** — behavioral probes only, iMessage-native, structured
  persona because downstream matching needs JSON.

Tone: founder memo, not academic.

### `docs/decisions.md` (ADR-lite)

Written *during* the build, not upfront. Each entry: **Context → Decision →
Consequence**. Expected ADRs (rewrite to match what actually happens):

- **ADR-001: Merged scoring + next-question into one LLM call**
- **ADR-002: Haiku for turns, Opus for synthesis**
- **ADR-003: Adaptive branching only after probe_weekend**

**Honesty rule:** if reality diverges from these framings, rewrite the ADR to
match what actually happened during the build. A video narrating a decision
that isn't reflected in the code is worse than no decision log.

### `docs/state-machine.md` (auto-generated)

Generated at build-time via `scripts/export_graph.py`:

```python
from app.agent.graph import build_graph
from pathlib import Path
graph = build_graph()
mermaid = graph.get_graph().draw_mermaid()
Path("docs/state-machine.md").write_text(f"# State Machine\n\n```mermaid\n{mermaid}\n```\n")
```

Commit the output. GitHub renders mermaid inline — one file to open in the
video's "how it's built" beat.

### `prompts/` directory — git log as iteration artifact

Each prompt in its own `.txt` file. When you refine one, commit the old
version first as its own commit, then commit the replacement separately.
For at least one prompt (likely `probe_weekend.txt`), this produces:

```
git log prompts/probe_weekend.txt
  commit ab12 "refine: more colloquial, stronger interest-mining hook"
  commit cd34 "first pass: formal phrasing"
```

Video beat: open terminal, `git log -p prompts/probe_weekend.txt`, show the
diff, narrate what changed and why.

### `README.md`

```
# Twin
> Onboarding agent that builds your digital double for Ditto's matchmaking.

[GIF of the persona reveal moment — record with Kap or Cleanshot post-build]

## What it does
[1 paragraph]

## Why this feature first
[condensed founder argument — 2 paragraphs]

## Run locally
[3 commands]

## Architecture
[embedded mermaid state machine, Channel abstraction callout]

## Research & decisions
→ docs/research.md
→ docs/decisions.md

## What's next (V2)
[full humor signal pitch + simulator + feedback agent]
```

The GIF at the top is the highest-leverage piece of README real estate.

---

## 6. Build order

**Principle: every phase ends in a working commit.** You should be able to
stop at any point and have a demoable artifact.

### Phase 0 — Lock the "why" before any code (~30 min)

Write `docs/research.md` first. Locks the founder argument the whole video
rests on. Also write README skeleton (sections, no content). Commit.

### Phase 1 — Scaffolding (~30 min)

`git init` the Twin directory (not yet a repo). Add `.gitignore`. Scaffold
FastAPI backend + Vite/React/TS/Tailwind frontend. Verify CORS. Commit.

### Phase 2 — Schemas (~20 min)

All Pydantic models (`Persona`, `Demographics`, `Personality`, `Interest`,
`Message`, `AgentState`, `ProbeOutput`, `InterestProbeOutput`). SQLAlchemy
models. TypeScript mirror in `frontend/src/types.ts`. Commit.

### Phase 3 — Channel abstraction (~15 min)

`Channel` ABC, `WebChannel`, `PhotonChannel` stub. Commit. **10-minute add
that carries 30 seconds of video.**

### Phase 4 — LangGraph skeleton (~30 min)

`greeting` + `demographics` nodes only. In-memory session state keyed by
session_id. Two endpoints working end-to-end.

**STOP. Wire the frontend to send/receive plain text. Verify round-trip works
with ugly unstyled bubbles.** If this doesn't work, nothing else matters.
Commit.

### Phase 5 — Interview nodes (~60–75 min, the prompt-iteration phase)

Add nodes one at a time, test each, commit each:

- `probe_weekend` (scoring probe — write v1 prompt, test, refine, commit v2 as a separate commit)
- `adaptive_interest` (conditional edge off `probe_weekend`, uses `InterestProbeOutput`)
- `probe_planning` (scoring probe, two dimensions)
- `probe_support` (scoring probe)
- `values_rank` (interview node, no scoring — user picks top 3 from 6 options)
- `dealbreakers` (interview node, no scoring — free-form list)

Small commits = readable git log. The scoring probes share `ProbeOutput`;
`values_rank` and `dealbreakers` are simple text-extraction nodes with their
own small schemas.

### Phase 6 — Synthesize + reveal (~30 min)

`synthesize` (Opus) produces full Persona JSON including `summary` and
`conversation_hooks`. `reveal` formats a message, no LLM call. Persist to
`sessions.persona_json`. `GET /sessions/{id}/persona` returns JSON. Commit.

### Phase 7 — Frontend polish (~60 min)

Tier 1 must-haves first (iMessage bubbles, typing indicator, composer, reveal
sheet, auto-scroll, Start-over). Tier 2 should-haves. Tier 3 only if time.
Commit.

### Phase 8 — Iteration artifacts + docs (~30 min)

Run `scripts/export_graph.py`. Write `decisions.md` based on *actual* build
experience. Finish README with mermaid embed and V2 roadmap. Record GIF of
reveal moment, drop at top of README. Commit.

### Phase 9 — One smoke test (~15 min)

Single Pytest: scripted 9-turn conversation with recorded Anthropic fixture
response, asserts valid Persona JSON. Commit.

### Phase 10 — Record the video (~60–90 min)

Script 5 beats, practice once, record twice, edit for time.

### Phase 11 (optional, last) — Deploy (~20–30 min)

Vercel + Railway polish, only if recording is done. If deploy breaks
unexpectedly, delete URL from README and ship local-only.

**Realistic total: ~6–8 hours active work.**

### Cut lines (in order — cut these if a phase blows up)

1. Dark mode (already cut — iMessage is light-only)
2. Bubble tail curl + timestamp separators (Tier 2 frontend)
3. *"Delivered"* text, haptic bounce (Tier 3)
4. Conversation hooks disclosure in reveal card (still compute, hide in UI)
5. `probe_support` — if it breaks, default `thinking = 0.5`, document in ADR
6. `adaptive_interest` — if conditional edges get weird, always transition
   straight through; accept all interests as `medium`-depth
7. Deploy (already cut by default)

### Non-negotiables (do not cut)

- The persona reveal card (cold-open of video)
- At least 2 of the 3 personality-scoring probes (`probe_weekend`, `probe_planning`, `probe_support`) — else the personality dimensions are too sparse to defend
- Channel abstraction
- `research.md` + `decisions.md`
- LangGraph diagram export
- Merged-call architecture

---

## 7. V2 roadmap

### Video beat (~30s)

> "V1 gives Ditto the structured persona. V2 adds the signal no other dating
> app is matching on: humor. Users react to a curated stimulus set — memes,
> tweets, clips — and those reactions become a humor-compatibility vector
> alongside the persona. Stronger than shared hobbies as a predictor, harder
> to fake, and not a feature in Hinge, Bumble, or Tinder. Also on deck: a
> persona-vs-persona simulation engine so Ditto's '1000 simulated dates'
> thesis becomes literal, and a post-date feedback agent that closes the
> learning loop."

### README long-form — humor signal (~350 words)

**Why humor is the next axis:** Shared sense of humor is one of the more
robust predictors of long-term relationship satisfaction (Gottman marriage-
stability research + Hall 2017 humor-in-romance meta-analysis — verify exact
claims when writing the doc). Stronger than shared hobbies. Revealed rather
than declared — you can lie about valuing family, you can't fake what makes
you laugh. No major dating app matches on a rigorous humor signal today.

**How it plugs into Twin (additive, not replacing):**
1. After the interview, user sees a curated stimulus set (20–30 items
   spanning dry, absurdist, wholesome, dark, observational, meme-native)
2. Reactions (laugh / smile / meh / cringe + reaction time) embed into a
   humor vector
3. Vector attaches to Persona, feeds Ditto's simulator alongside personality
   + values + interests

**Why V2, not V1:** Twin is upstream infrastructure. Humor-matching assumes
users + personas + matching already exist. Sequencing, not compromise.

### Other V2+ candidates (README-mentioned, not video-pitched)

- **Persona-vs-persona simulation engine** — two LLM agents with different
  personas run a simulated first date, a judge agent scores chemistry. The
  "1000 simulated dates" thesis made literal. Twin's persona schema consumes
  as-is.
- **Post-date feedback agent** — after a real date, Twin texts user to extract
  qualitative feedback, updates persona, retrains simulator's judge. Closes
  Ditto's learning loop. Twin graduates from one-shot onboarding into a
  lifecycle agent.

**Ordering logic:** humor (user-visible differentiation with research base)
→ simulator (cheap once Twin exists, unblocks Ditto's core marketing claim)
→ feedback agent (requires real dates + time).

---

## 8. Out of scope

### Product surface
- User authentication / login (session_id is the only identity)
- Mobile responsive / mobile browser support (desktop-only demo)
- Session resumption across page refresh (memory-only on client)
- User-editable persona (read-only reveal)
- Skip / back buttons mid-interview (Start-over resets the whole thing)
- Persona history / account dashboard

### Platform / infra
- Postgres, Neon, or managed DB (SQLite file)
- Deploy pipeline (optional Phase 11 only)
- Docker / docker-compose
- WebSockets / streaming responses
- CI/CD, GitHub Actions, pre-commit hooks

### Robustness / ops
- Error handling beyond `alert("something went wrong")`
- Rate limiting / abuse protection
- Anthropic API failover / caching / retry logic
- Analytics, tracking, Sentry / PostHog
- Tests beyond one e2e smoke test

### AI / agent surface
- Humor signal (V2 — named only)
- Matching engine / simulator / date proposer (V2+ — named only)
- Post-date feedback agent (V2+ — named only)
- Real Photon Spectrum SDK integration (stub only)
- Sonnet fallback plumbing (documentational until Haiku fails)
- Multi-language / i18n
- Accessibility audit (sensible defaults only, no WCAG pass)

### Privacy / compliance (named, not built)
- GDPR / CCPA data deletion endpoints
- Consent banner, privacy policy
- API key rotation / secret manager

---

## Open items to verify when writing docs

- Finkel & Eastwick meta-analysis exact claim on demographic-vs-behavioral
  matching (for `research.md`)
- Gottman humor-in-relationships citation (for `research.md` V2 section)
- Hall 2017 humor meta-analysis exact claim (for V2 section)
- Anthropic Haiku 4.5 conversational texture quality — 5-minute smoke test
  at build-start to confirm it passes the iMessage-feel bar

---

*End of spec. Next step: invoke writing-plans skill to produce the
step-by-step implementation plan.*
