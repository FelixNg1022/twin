from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    demographics_node,
    greeting_node,
    probe_weekend_node,
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
    builder.add_edge("probe_weekend", END)  # temporary — extended in Task 5.3

    checkpointer = MemorySaver()
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["collect_demographics", "probe_weekend"],
    )
