# Twin — Build Spec

*The onboarding agent that creates your digital double for Ditto's matchmaking engine.*

## Context
Building a take-home project for Ditto AI (ditto.ai), an iMessage-based AI
matchmaker for college students. They do NOT have swiping, profiles, or in-app
chat. Users text an AI agent their preferences, the agent builds a persona,
the backend simulates matches, and one date is proposed per week.

This project builds the **first feature**, called **Twin**: a conversational
AI that onboards a new user by interviewing them, extracting personality +
values + interests, and outputting a structured persona object — the user's
"digital twin" — that downstream matching consumes.

The name ties directly to Ditto's core thesis: the AI persona "dates 1000
times" in simulation before humans meet. Twin is the feature that creates
that digital double.

Time budget: ~90 minutes of active coding. Ruthless scoping required.

## Core thesis
MBTI is not scientifically rigorous, but users self-identify with it and find
it fun. Big Five dimensions predict relationship compatibility better. The
agent probes using behavioral questions that score against Big Five-adjacent
dimensions under the hood, then returns an MBTI label + continuous dimension
scores + interest graph + ranked values + dealbreakers.

The agent must NEVER ask direct MBTI questions ("do you prefer logic or
feelings"). It asks behavioral prompts and scores from the response.

## Non-negotiable product design choices
1. Frontend MUST look like iMessage (blue outbound bubbles, grey inbound,
   SF Pro font, rounded corners, no chrome). This is a culture signal to Ditto.
2. Agent responses must feel like texts, not form prompts. Short, lowercase
   okay, natural phrasing. No "Please describe your ideal partner."
3. Adaptive follow-ups: if user mentions a specific interest (hiking, music,
   gaming, cooking), the agent must branch and dig one level deeper before
   returning to the main flow.
4. Final output is a structured JSON persona, shown to the user at the end
   ("here's what I learned about you") AND logged to the backend.

## Architecture

### Stack
- Backend: FastAPI (Python 3.11+), uvicorn
- Agent orchestration: LangGraph
- LLM: Anthropic SDK (claude-sonnet-4-5 or claude-opus-4-7)
- Persistence: SQLite via SQLAlchemy (single file, zero setup)
- Frontend: Vite + React 19 + TypeScript + Tailwind v3
- HTTP: fetch to FastAPI endpoints, no websockets (keep it simple)

### Channel abstraction (important for the video)
Wrap message send/receive in a `Channel` interface with two implementations:
- `WebChannel` (what the demo uses, backed by FastAPI POST endpoints)
- `PhotonChannel` (stub only — just a class with the right method signatures
  and a comment pointing to Photon Spectrum SDK docs)

This is a 10-minute add that pays huge dividends in the video. The point is to
show that agent logic is decoupled from delivery channel.

### Directory layout
```
twin/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app, CORS, routes
│   │   ├── agent/
│   │   │   ├── graph.py          # LangGraph state machine
│   │   │   ├── nodes.py          # Individual node implementations
│   │   │   ├── prompts.py        # System prompts per node
│   │   │   └── state.py          # Pydantic state schema
│   │   ├── channels/
│   │   │   ├── base.py           # Channel ABC
│   │   │   ├── web.py            # WebChannel (used)
│   │   │   └── photon.py         # PhotonChannel stub
│   │   ├── models/
│   │   │   ├── persona.py        # Pydantic Persona schema
│   │   │   └── db.py             # SQLAlchemy models
│   │   └── scoring.py            # Dimension scoring from responses
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.tsx
    │   ├── components/
    │   │   ├── IMessageBubble.tsx
    │   │   ├── ChatWindow.tsx
    │   │   ├── ComposerBar.tsx
    │   │   └── PersonaReveal.tsx
    │   ├── hooks/
    │   │   └── useChat.ts
    │   └── types.ts
    ├── package.json
    └── tailwind.config.js
```

## Persona output schema

```python
class Persona(BaseModel):
    user_id: str
    demographics: Demographics
    personality: Personality
    values_ranked: list[str]          # top 3 from a fixed vocabulary
    interests: list[Interest]
    dealbreakers: list[str]
    conversation_hooks: list[str]     # 3 specific details a matched partner could open with
    created_at: datetime

class Demographics(BaseModel):
    age: int
    gender: str
    sexual_orientation: str
    campus: str
    travel_radius_km: int

class Personality(BaseModel):
    mbti: str                          # "ENFP", etc — derived from dimensions
    dimensions: PersonalityDimensions

class PersonalityDimensions(BaseModel):
    # continuous scores 0.0 to 1.0
    # higher = first letter (E, N, T, J)
    extraversion: float
    intuition: float
    thinking: float
    judging: float

class Interest(BaseModel):
    topic: str                         # "hiking"
    depth_signal: Literal["low", "medium", "high"]
    specific_details: str              # "solo multi-day trips, last one West Coast Trail"
```

## LangGraph state machine

State:
```python
class AgentState(BaseModel):
    user_id: str
    messages: list[Message]            # full conversation history
    current_node: str
    demographics: Demographics | None
    dimension_scores: dict[str, list[float]]  # accumulated evidence per dimension
    interests_mentioned: list[Interest]
    values_probed: list[str]
    dealbreakers: list[str]
    complete: bool
```

Nodes (in order):
1. `greeting` — welcome + get first name
2. `demographics` — age, gender, orientation, campus (one at a time, conversational)
3. `probe_weekend` — "what did you do last saturday night?" (E/I signal + interest mining)
4. `adaptive_interest` — if interest mentioned, branch and ask one follow-up. LLM decides if mentioned.
5. `probe_planning` — "how do you plan a trip?" (S/N + J/P signal)
6. `probe_support` — "a friend just went through a breakup, what do you say first?" (T/F signal)
7. `values_rank` — agent surfaces 6 values ("ambition, family, adventure, growth, stability, creativity") and asks user to pick top 3 in order
8. `dealbreakers` — "anything that's an instant no?"
9. `synthesize` — LLM converts accumulated state into final Persona JSON
10. `reveal` — send persona summary back as a message ("here's what I learned...")

Each probe node:
- Sends a question via the channel
- Waits for user response
- Passes the response to a scoring function that updates dimension_scores
- Runs adaptive-interest detection in parallel (does the response mention a
  hobby/topic worth digging into?)
- Transitions to next node

## Scoring approach
For each probe, use Claude with structured output to score the response:

```python
async def score_response(
    question_dimension: str,        # e.g. "extraversion"
    user_response: str,
) -> dict:
    """Returns {score: float, evidence: str, interests_detected: list[str]}"""
    # structured output call to Claude
    # score is 0.0 to 1.0, higher = first-letter trait
```

Final MBTI letter derivation:
- `E` if avg(extraversion) >= 0.5 else `I`
- `N` if avg(intuition) >= 0.5 else `S`
- `T` if avg(thinking) >= 0.5 else `F`
- `J` if avg(judging) >= 0.5 else `P`

## API surface

```
POST /sessions                    → create session, returns user_id + first agent message
POST /sessions/{id}/messages      → send user message, returns agent reply(ies) + state
GET  /sessions/{id}/persona       → get final persona (only valid after complete)
```

Responses include a `complete: bool` flag so the frontend knows when to
render the persona reveal UI.

## Frontend requirements

- iMessage aesthetic: grey inbound bubbles (#e5e5ea bg, black text), blue
  outbound (#007aff bg, white text), tail on last bubble of each sender's run,
  timestamps grouped by minute, SF Pro Display / -apple-system font stack
- Typing indicator (three animated dots) while waiting for agent response
- Auto-scroll to bottom on new message
- Composer bar pinned to bottom with rounded input + blue send button
- On `complete: true`, slide up a bottom sheet showing the structured persona
  as a nicely formatted card (MBTI letter big, dimension bars, interests as
  chips, values as ranked list)
- No auth, no login screen — just start a session on page load

## Out of scope (explicitly skip)
- User authentication
- Postgres or Neon (use SQLite)
- Deploy pipeline (handle separately after build)
- Unit tests beyond one end-to-end smoke test that runs the graph with
  scripted user responses
- Error handling beyond "show an alert"
- Mobile responsive design (desktop web only for demo)
- Multi-user matching — persona only
- Photon SDK real integration — stub class only

## Build order (strict)
1. Scaffold backend (FastAPI hello world) + frontend (Vite + Tailwind hello world)
2. Pydantic schemas (Persona, AgentState, Message)
3. Channel ABC + WebChannel
4. LangGraph state graph with greeting + demographics nodes only
5. Wire frontend to backend, verify round-trip messaging works
6. Add remaining probe nodes one by one, confirming each before moving on
7. Scoring function + MBTI derivation
8. Synthesis node + persona reveal endpoint
9. iMessage styling polish (bubbles, typing indicator, reveal sheet)
10. PhotonChannel stub with doc comment
11. Single smoke test: scripted 9-turn conversation produces valid Persona JSON

Stop the moment any step takes >15 min to debug. Cut the feature, move on.

## .env.example
```
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-opus-4-7
DATABASE_URL=sqlite:///./twin.db
CORS_ORIGINS=http://localhost:5173
```

## V2 roadmap — document in README, don't build

The README Claude Code generates should include a "What's next" section
describing the planned V2 feature: **humor-based compatibility signal**.

### Why humor is the next axis
Shared sense of humor is one of the more robust predictors of long-term
relationship satisfaction in the research literature — stronger than shared
hobbies or demographic similarity. It's also harder to fake than self-reported
values: humor is revealed through reaction, not declared through text. No
major dating app (Hinge, Bumble, Tinder) matches on a rigorous humor signal
today, so it's a real differentiation opportunity for Ditto.

### How it plugs into Twin
Twin V1 outputs a structured persona (MBTI + dimensions + values + interests +
dealbreakers). V2 adds a parallel signal layer:
1. After the Twin interview completes, user is shown a curated stimulus set
   (memes, tweet screenshots, short clips) and reacts to each (laugh / smile /
   meh / cringe + optional timing data)
2. Reactions are embedded into a humor vector per user
3. The vector is attached to the persona and fed into Ditto's matching
   simulation alongside the existing persona fields — humor compatibility
   becomes an additional scoring dimension, not a replacement

### Why it's V2 not V1
Twin is upstream infrastructure — without a persona, no matching feature works.
Humor-matching assumes users + personas + a matching layer already exist, so
it's a feature that builds on Twin, not one that replaces it. Building Twin
first is the correct architectural sequencing.

### Other V2+ candidates worth naming briefly
- **Persona-vs-persona simulation engine** — two LLM agents with different
  personas run a simulated first date, a judge agent scores chemistry. This
  is Ditto's stated "1000 simulated dates" secret sauce made real.
- **Post-date feedback agent** — after a real date, Twin texts the user to
  extract rich qualitative feedback and updates the persona. Closes the
  learning loop Ditto's founders describe in press.

## Ghost mode
Build clean code with short, purposeful comments only where intent is
non-obvious. No docstring boilerplate. No console.log debug spam left in.
No TODO comments — either do it or cut it from scope.
