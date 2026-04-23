from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    adaptive_interest_node,
    dealbreakers_node,
    demographics_node,
    greeting_node,
    probe_planning_node,
    probe_stress_node,
    probe_support_node,
    probe_weekend_node,
    reveal_node,
    synthesize_node,
    values_rank_node,
)
from app.agent.state import AgentState


def _demographics_router(state: AgentState) -> str:
    if state.demographics_pending_field is None:
        return "probe_weekend"
    return "collect_demographics"


def _weekend_router(state: AgentState) -> str:
    target = state.current_node
    if target in ("adaptive_interest", "probe_planning"):
        return target
    return "probe_weekend"


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("greeting", greeting_node)
    builder.add_node("collect_demographics", demographics_node)
    builder.add_node("probe_weekend", probe_weekend_node)
    builder.add_node("adaptive_interest", adaptive_interest_node)
    builder.add_node("probe_planning", probe_planning_node)
    builder.add_node("probe_support", probe_support_node)
    builder.add_node("probe_stress", probe_stress_node)
    builder.add_node("values_rank", values_rank_node)
    builder.add_node(
        "ask_dealbreakers", dealbreakers_node
    )  # renamed to avoid clash with state.dealbreakers
    builder.add_node("synthesize", synthesize_node)
    builder.add_node("reveal", reveal_node)

    builder.set_entry_point("greeting")
    builder.add_edge("greeting", "collect_demographics")
    builder.add_conditional_edges(
        "collect_demographics",
        _demographics_router,
        {
            "collect_demographics": "collect_demographics",
            "probe_weekend": "probe_weekend",
        },
    )
    builder.add_conditional_edges(
        "probe_weekend",
        _weekend_router,
        {
            "probe_weekend": "probe_weekend",
            "adaptive_interest": "adaptive_interest",
            "probe_planning": "probe_planning",
        },
    )
    builder.add_edge("adaptive_interest", "probe_planning")
    builder.add_edge("probe_planning", "probe_support")
    builder.add_edge("probe_support", "probe_stress")
    builder.add_edge("probe_stress", "values_rank")
    builder.add_edge("values_rank", "ask_dealbreakers")
    builder.add_edge("ask_dealbreakers", "synthesize")
    builder.add_edge("synthesize", "reveal")
    builder.add_edge("reveal", END)

    checkpointer = MemorySaver()
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=[
            "collect_demographics",
            "probe_weekend",
            "adaptive_interest",
            "probe_planning",
            "probe_support",
            "probe_stress",
            "values_rank",
            "ask_dealbreakers",
            # synthesize + reveal fire inline after dealbreakers — not interrupted
        ],
    )
