from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agent.nodes import demographics_node, greeting_node
from app.agent.state import AgentState


def _demographics_router(state: AgentState) -> str:
    if state.demographics_pending_field is None:
        # All demographics filled — in Phase 4 we just END; later phases route to probe_weekend.
        return END
    return "collect_demographics"


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("greeting", greeting_node)
    builder.add_node("collect_demographics", demographics_node)

    builder.set_entry_point("greeting")
    builder.add_edge("greeting", "collect_demographics")
    builder.add_conditional_edges(
        "collect_demographics",
        _demographics_router,
        {END: END, "collect_demographics": "collect_demographics"},
    )

    checkpointer = MemorySaver()
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["collect_demographics"],
    )
