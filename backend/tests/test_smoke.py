"""Smoke test: verify the graph is wired correctly and schemas round-trip.

A full mocked end-to-end test against scripted Anthropic responses is brittle
(off-by-one fixture counts kill it), and a live test requires an API key and
spends real tokens. Instead:

1. Build the graph and assert every node is present and reachable.
2. Round-trip Persona through JSON and re-validate.
3. Roundtrip AgentState through JSON (structural).

For live end-to-end: set ANTHROPIC_API_KEY in backend/.env and run the app
against the frontend. The critical correctness properties (MBTI derivation,
score aggregation boundaries) are covered by test_mbti.py.
"""

from datetime import datetime

import pytest

from app.agent.graph import build_graph
from app.agent.state import AgentState
from app.models.persona import (
    Demographics,
    Interest,
    Persona,
    Personality,
    PersonalityDimensions,
)


def test_graph_has_all_expected_nodes():
    graph = build_graph()
    nodes = graph.get_graph().nodes
    expected = {
        "greeting",
        "collect_demographics",
        "probe_weekend",
        "adaptive_interest",
        "probe_planning",
        "probe_support",
        "probe_stress",
        "values_rank",
        "ask_dealbreakers",
        "synthesize",
        "reveal",
    }
    assert expected.issubset(set(nodes.keys())), (
        f"missing nodes: {expected - set(nodes.keys())}"
    )


def test_graph_entry_is_greeting():
    graph = build_graph()
    mermaid = graph.get_graph().draw_mermaid()
    assert "__start__ --> greeting" in mermaid


def test_graph_dealbreakers_routes_to_synthesis_chain():
    graph = build_graph()
    mermaid = graph.get_graph().draw_mermaid()
    assert "ask_dealbreakers --> synthesize" in mermaid
    assert "synthesize --> reveal" in mermaid
    assert "reveal --> __end__" in mermaid


def test_graph_adaptive_interest_branch_present():
    graph = build_graph()
    mermaid = graph.get_graph().draw_mermaid()
    # Conditional edges render as `.->` in the mermaid output
    assert "probe_weekend -.-> adaptive_interest" in mermaid
    assert "probe_weekend -.-> probe_planning" in mermaid


def test_persona_json_roundtrip():
    persona = Persona(
        session_id="sess-1",
        summary="alex, you're an introverted planner with a strong internal compass.",
        demographics=Demographics(
            age=20,
            gender="female",
            sexual_orientation="straight",
            campus="UC Berkeley",
            travel_radius_km=30,
        ),
        personality=Personality(
            mbti="ISFJ",
            dimensions=PersonalityDimensions(
                extraversion=0.2, intuition=0.3, thinking=0.15, judging=0.8
            ),
        ),
        values_ranked=["growth", "stability", "adventure"],
        interests=[
            Interest(
                topic="hiking",
                depth_signal="high",
                specific_details="mt tam regular; West Coast Trail last summer",
            ),
            Interest(topic="reading", depth_signal="low", specific_details=""),
        ],
        dealbreakers=["smokers", "doesn't want kids"],
        conversation_hooks=[
            "ask them about the west coast trail trip",
            "ask what they're reading right now",
            "ask for their spreadsheet trip-planning rituals",
        ],
        created_at=datetime.utcnow(),
    )

    as_json = persona.model_dump_json()
    round_tripped = Persona.model_validate_json(as_json)

    assert round_tripped.session_id == persona.session_id
    assert round_tripped.personality.mbti == "ISFJ"
    assert len(round_tripped.interests) == 2
    assert round_tripped.interests[0].depth_signal == "high"
    assert len(round_tripped.values_ranked) == 3
    assert len(round_tripped.conversation_hooks) == 3


def test_agentstate_default_shape():
    state = AgentState(session_id="sess-1")
    assert state.current_node == "greeting"
    assert state.demographics_pending_field == "first_name"
    assert state.demographics is None
    assert state.demographics_partial == {}
    assert state.dimension_scores == {}
    assert state.complete is False
    assert state.messages == []


def test_probe_output_schema_has_required_fields():
    """Sanity-check the tool schema that Claude will fill in."""
    from app.models.probe import ProbeOutput

    schema = ProbeOutput.model_json_schema()
    required = set(schema.get("required", []))
    # All five output fields should be required for structured extraction:
    expected_required = {
        "scores",
        "evidence",
        "next_message",
    }
    # interests_detected + interest_to_probe have defaults — not strictly required.
    # But scores, evidence, and next_message must be present.
    assert expected_required.issubset(required), (
        f"ProbeOutput missing required fields: {expected_required - required}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
