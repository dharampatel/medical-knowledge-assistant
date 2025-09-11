from langgraph.graph import StateGraph, END
from app.state import AgentState

from app.nodes import (
    classify_node,
    off_domain_node,
    retrieve_with_refine_node,
    summarize_node,
    explain_node,
    no_answer_node, fetch_trials_node,
)


def build_workflow():
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("classify", classify_node)
    workflow.add_node("off_domain", off_domain_node)
    workflow.add_node("retrieve_refine", retrieve_with_refine_node)
    workflow.add_node("fetch_trials", fetch_trials_node)  # New node
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("explain", explain_node)
    workflow.add_node("no_answer", no_answer_node)

    # Entry point
    workflow.set_entry_point("classify")

    # Branch: off-domain vs medical
    workflow.add_conditional_edges(
        "classify",
        lambda state: "off_domain" if state["domain"] == "other" else "retrieve_refine",
        {"off_domain": "off_domain", "retrieve_refine": "retrieve_refine"},
    )
    workflow.add_edge("off_domain", END)

    # Retrieval & refinement logic handled inside retrieve_with_refine_node
    workflow.add_conditional_edges(
        "retrieve_refine",
        lambda state: (
            "fetch_trials" if state.get("docs") else "no_answer"
        ),
        {"fetch_trials": "fetch_trials", "no_answer": "no_answer"},
    )

    # Fetch trials → Summarize
    workflow.add_edge("fetch_trials", "summarize")

    # Final paths
    workflow.add_edge("summarize", "explain")
    workflow.add_edge("explain", END)
    workflow.add_edge("no_answer", END)

    return workflow.compile()

