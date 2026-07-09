from langgraph.graph import StateGraph, END

from state import CollegeState
from nodes import (
    intent_node,
    college_info_node,
    exam_node,
    fees_node,
    scholarship_node,
)


def route_intent(state: CollegeState) -> str:
    """Route to specialized node based on classified intent."""
    intent = state.get("intent", "").strip().lower()
    if "college_info" in intent:
        return "college_info"
    elif "exam" in intent:
        return "exam"
    elif "fee" in intent:
        return "fees"
    elif "scholarship" in intent:
        return "scholarship"
    return "college_info"  # Default fallback


workflow = StateGraph(CollegeState)

# Add all nodes
workflow.add_node("intent", intent_node)
workflow.add_node("college_info", college_info_node)
workflow.add_node("exam", exam_node)
workflow.add_node("fees", fees_node)
workflow.add_node("scholarship", scholarship_node)

# Set starting point
workflow.set_entry_point("intent")

# Add conditional routing
workflow.add_conditional_edges(
    "intent",
    route_intent,
    {
        "college_info": "college_info",
        "exam": "exam",
        "fees": "fees",
        "scholarship": "scholarship",
    },
)

# Connect specialized nodes to END
workflow.add_edge("college_info", END)
workflow.add_edge("exam", END)
workflow.add_edge("fees", END)
workflow.add_edge("scholarship", END)

# Compile graph
graph = workflow.compile()
