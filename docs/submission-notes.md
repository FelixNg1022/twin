# Anything else you'd like us to know?

Hi Ditto team,

A few architectural and design details I couldn't fit into the video — hoping this rounds out the full picture.

## Customer research opener

I talked to friends who actively use dating apps and surfaced two recurring pain points — fake profiles / catfishing, and personality-incompatible dates. Ditto's model structurally solves the first (no profile = nothing to fake), and Twin specifically attacks the second by scoring Big Five under the hood.

## Architecture

- LangGraph state machine, 11 nodes, one conditional branch (adaptive hiking follow-up). Full mermaid diagram: `docs/state-machine.md`.
- Each probe node makes ONE structured-output Claude call that returns BOTH the dimension scores and the next question. Halves per-turn latency vs. the naive two-call design.
- Haiku 4.5 for every in-turn call; Opus 4.7 only for synthesis. Two env vars, so swapping to Sonnet as a fallback is a one-line change.
- Channel abstraction: `WebChannel` (demo) + `PhotonChannel` (stub). Nodes call `channel.deliver(...)` without knowing the delivery layer — agent logic is portable the day Ditto wires Photon Spectrum.

## Iteration evidence

- `probe_weekend` went through a visible v1→v2 rewrite, committed as separate commits. v1 was too formal and pulled generic answers; v2 pulled texture-rich specifics like the hiking follow-up you saw in the demo. `git log --oneline backend/prompts/probe_weekend.txt` shows the commits.
- Mid-build, I threw out LangGraph's built-in checkpointer when its state-merge semantics broke the demographics transition. Hand-rolled a session runner instead. Documented as ADR-005 in `docs/decisions.md`.

## Big Five as the ground truth

Twin probes all five Big Five factors, including Neuroticism via a dedicated stress probe (which has no MBTI equivalent — most MBTI-derived products skip it entirely). The MBTI letter is derived from 4 of the 5. Toggle on the reveal card shows both views: MBTI for cultural share-ability, Big Five for scientific ground truth.

## Full documentation

- Design spec: `docs/superpowers/specs/2026-04-22-twin-design.md`
- 42-task implementation plan: `docs/superpowers/plans/2026-04-23-twin-implementation.md`
- Decisions log (5 ADRs): `docs/decisions.md`
- Customer research memo: `docs/research.md`

Happy to walk through any part of this in more depth.

— Felix
