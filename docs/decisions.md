# Decisions

Lightweight ADR log. Context → Decision → Consequence.

## ADR-001: Merge scoring + next-question into one Claude call per probe

**Context.** The initial spec had each probe node make two sequential Claude calls per turn — one to score the user's response, one to generate the next question. With Opus, this would have produced 3–6 seconds of wait between messages, which breaks the iMessage-feel the product requires.

**Decision.** Each probe node makes one structured-output call that returns `{scores, evidence, interests_detected, interest_to_probe, next_message}`. The scoring rubric and the question generator share a single prompt. The helper is in `backend/app/services/structured_call.py` and uses Anthropic's tool-use API with `tool_choice={"type": "tool", "name": ...}` to force a specific structured output.

**Consequence.** Per-turn latency halved vs. the two-call design. Scoring logic and question phrasing live in the same file (`backend/prompts/probe_*.txt`), which forces you to think about both at once — in practice that made the prompts sharper. Downside: if we ever want to change scoring without touching question generation, we have to edit both concerns in the same prompt. Accepted.

## ADR-002: Haiku for in-turn calls, Opus only for synthesis

**Context.** A chat UX with 10-turn latency budget made Opus-everywhere infeasible. Even one Opus call per turn felt sluggish (~4s in practice). Sonnet was considered as a middle ground but Haiku 4.5 handled the conversational texture and scoring well enough that the extra Sonnet cost wasn't justified.

**Decision.** `ANTHROPIC_TURN_MODEL=claude-haiku-4-5-20251001` for every probe + interview node. `ANTHROPIC_SYNTHESIS_MODEL=claude-opus-4-7` for the one-shot `synthesize` call. Config split into two env vars so the fallback (Haiku → Sonnet) is a one-line change.

**Consequence.** Per-turn latency now ~500–800ms, which reads as iMessage-feel. Synthesize still takes 10–15s, but that's hidden behind the `"putting your twin together..."` typing indicator — users expect a beat before a reveal. Reserving Opus for the single call where it matters keeps costs low and UX fast.

## ADR-003: Adaptive branching only after `probe_weekend`

**Context.** The first sketch let any probe fire an interest-follow-up. That stretched the interview to 13+ turns in testing and introduced ambiguity about which probe's scoring path to take after a branch. The onboarding completion rate matters: college dating apps tend to lose users in long onboarding.

**Decision.** Only `probe_weekend` produces `interest_to_probe`. Other probes collect interest mentions passively into `state.interests_detected`, but never branch. The graph edge `probe_weekend → adaptive_interest` is conditional; all other probes use plain sequential edges.

**Consequence.** Predictable ~10-turn interview. State machine stays readable (see `docs/state-machine.md`). Only one interest ever reaches `depth_signal: "high"`; the rest are `medium` or `low` based on how concretely they surfaced in the transcript.

## ADR-004: `ask_dealbreakers` node name (vs. `dealbreakers`)

**Context.** LangGraph requires node names not collide with state field names. `AgentState` has a `dealbreakers: list[str]` field, so a node literally named `dealbreakers` throws `ValueError: 'dealbreakers' is already being used as a state key` at `StateGraph.add_node()`. Same issue earlier with a node named `demographics` vs. `state.demographics: Demographics | None`.

**Decision.** Rename the final interview node to `ask_dealbreakers`. Renamed the demographics-collection node to `collect_demographics` earlier for the same reason.

**Consequence.** Slight inconsistency between the function name (`dealbreakers_node`) and the graph node name (`ask_dealbreakers`), but it's a one-line comment in `graph.py` to explain. State field semantics (`state.dealbreakers` = the collected list) and node semantics (`ask_dealbreakers` = the action of asking) are arguably more accurate anyway.
