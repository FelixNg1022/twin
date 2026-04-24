# Twin

> An onboarding agent that creates your digital double for Ditto's matchmaking engine.

<p align="center">
  <img src="docs/reveal.gif" alt="Twin persona reveal — ISFJ card springs up with continuous dimension scores" width="360" />
</p>

Take-home for Ditto AI's engineering internship. The prompt: *"if you're Ditto's founder, what's the first feature you'd build?"*

---

## Why Twin first

Before writing a line of code I asked several friends who actively use dating apps what actually breaks the experience. Two pain points came up every time:

1. **Fake profiles / catfishing** — people curate themselves into someone they're not, or use photos that aren't them
2. **Personality mismatch** — even when the match is real, dates rarely click deeper than shared hobbies

Ditto's whole model attacks both at the root. There *is* no profile — an AI represents you, built from how you actually behave, so there's nothing to catfish. And if matching can happen on real personality signal instead of vibes, the second pain goes away too.

But that only works if the AI has an accurate *you* to represent. So the first feature can't be the matcher or the date proposer — it has to be **the one that builds the persona**. That's Twin.

Full customer-research + design argument in [`docs/research.md`](docs/research.md).

---

## What it does

Twin is a conversational AI that interviews a new user over ~11 iMessage-style turns and outputs a **structured persona** downstream matching consumes. Under the hood it scores all five Big Five factors through dedicated behavioral probes; on the surface it shows an MBTI label users can screenshot and share.

The persona includes:

- MBTI letter + 5 continuous Big Five dimension scores with evidence traces
- Ranked top 3 values, dealbreakers
- Interests graph with depth signals (adaptive branching digs deeper into distinctive interests)
- 3 specific conversation hooks a matched partner could open with

Design choice that matters: Twin never asks direct personality questions ("are you extraverted?"). Self-report is noisy. Instead it asks behavioral prompts ("what'd you get up to Saturday night?" / "a friend just went through a breakup — what's the first thing you'd say?") and scores the response.

---

## Architecture

The agent is a **LangGraph state machine** — 11 nodes, one conditional edge.

```text
greeting → collect_demographics → probe_weekend → [adaptive_interest?]
  → probe_planning → probe_support → probe_stress → values_rank
  → ask_dealbreakers → synthesize → reveal
```

Mermaid diagram: [`docs/state-machine.md`](docs/state-machine.md).

### Key design choices

- **Big Five is the ground truth; MBTI is a derived wrapper.** All five Big Five factors are probed behaviorally (including Neuroticism via a dedicated stress probe — no MBTI equivalent). The MBTI letter is thresholded from 4 of the 5 for cultural share-ability. Toggle on the reveal card swaps between views.
- **Merged structured-output Claude call per probe.** Each probe node makes *one* call that returns dimension scores AND the next question in a single response. Halves per-turn latency vs. a two-call design and keeps scoring rubric co-located with question generation.
- **Haiku 4.5 for every in-turn call; Opus 4.7 for synthesis only.** Two env vars, so swapping to Sonnet as a fallback is a one-line change. Fastest model where the user is waiting, smartest where they aren't.
- **`Channel` abstraction.** `WebChannel` (buffers into HTTP response) and `PhotonChannel` (stub for Ditto's real iMessage delivery). Nodes call `channel.deliver(...)` without knowing the delivery layer — agent logic is portable the day Photon Spectrum gets wired.
- **Evidence-traceable scoring.** Every probe's dimension score is persisted to SQLite alongside a one-line evidence string from the LLM. `sqlite3 backend/twin.db "select * from scores"` shows the full audit trail.

### Stack

- Backend: FastAPI, LangGraph, Anthropic SDK, SQLAlchemy + SQLite, Pydantic v2
- Frontend: Vite, React 19, TypeScript, Tailwind v3
- Testing: pytest (unit + e2e smoke), ruff, eslint, TypeScript strict

---

## Iteration evidence

Three places to see this in action:

- **`backend/prompts/probe_weekend.txt`** went through a visible v1→v2 rewrite — v1 was too formal ("what did you do this past weekend?") and pulled generic answers; v2 ("what'd you get up to saturday night?") pulled texture-rich specifics. `git log --oneline backend/prompts/probe_weekend.txt` shows the two commits.
- **[`docs/decisions.md`](docs/decisions.md)** — 5 ADRs documenting non-obvious decisions. Notably ADR-005: mid-build I threw out LangGraph's built-in checkpointer when its state-merge semantics broke demographics transitions, and hand-rolled a session runner instead.
- **Specs + plan trail** — [`docs/superpowers/specs/2026-04-22-twin-design.md`](docs/superpowers/specs/2026-04-22-twin-design.md) is the 650-line design spec; [`docs/superpowers/plans/2026-04-23-twin-implementation.md`](docs/superpowers/plans/2026-04-23-twin-implementation.md) is the 42-task implementation plan. Spec → plan → execution is visible in the commit history.

---

## Run locally

You need Python 3.11 or 3.12 (3.14 breaks `pydantic-core` wheels at the time of writing), Node 18+, and an Anthropic API key.

Backend (one shell):

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

Frontend (another shell):

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Tests

```bash
cd backend && .venv/bin/pytest tests/ -v
```

12 tests covering MBTI derivation edge cases, graph topology, schema round-trips, and the tool-use output contract. One dedicated end-to-end smoke test verifies the graph wires correctly without spending real Anthropic tokens.

---

## What's next (V2)

### Humor-based compatibility

Shared sense of humor is one of the more robust predictors of long-term relationship satisfaction (Gottman's marriage-stability research; Hall 2017 meta-analysis on humor in romance). Stronger than shared hobbies, and harder to fake — you can lie about valuing family, you can't fake what makes you laugh. No major dating app matches on a rigorous humor signal today.

**Plug-in:** after the interview, the user reacts to a curated stimulus set (20–30 items spanning dry / absurdist / wholesome / dark / observational / meme-native). Reactions embed into a humor vector alongside the existing persona and feed Ditto's matcher additively.

### Simulation engine

Two LLM agents with different personas run a simulated first date; a judge agent scores chemistry. The "1000 simulated dates" thesis made literal. Twin's persona schema consumes as-is.

### Post-date feedback agent

After a real date, Twin texts the user to extract qualitative feedback, updates the persona, retrains the simulator's judge. Twin graduates from one-shot onboarding into a lifecycle agent.

Ordering logic: humor (user-visible differentiation with research base) → simulator (cheap once Twin exists, unblocks Ditto's marketing claim) → feedback agent (requires real dates + time).

---

## Further reading

| Doc | What's in it |
|-----|--------------|
| [`docs/research.md`](docs/research.md) | Founder memo — pain points, why self-report fails, why MBTI + Big Five together, design implications |
| [`docs/decisions.md`](docs/decisions.md) | 5 ADRs — merged call, model routing, adaptive branching, node naming, LangGraph checkpointer replacement |
| [`docs/state-machine.md`](docs/state-machine.md) | Auto-generated mermaid diagram of the full graph |
| [`docs/superpowers/specs/2026-04-22-twin-design.md`](docs/superpowers/specs/2026-04-22-twin-design.md) | Full design spec |
| [`docs/superpowers/plans/2026-04-23-twin-implementation.md`](docs/superpowers/plans/2026-04-23-twin-implementation.md) | 42-task implementation plan |

---

## Out of scope (named, not built)

No authentication, no mobile responsive, no tests beyond unit + e2e smoke, no real Photon SDK integration, no error handling beyond alerts, no deploy pipeline. See the design spec's "Out of scope" section for the full list.
