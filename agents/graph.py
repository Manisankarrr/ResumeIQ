from langgraph.graph import StateGraph

from agents.state import ScreenerState, default_state
from agents.nodes import node_extract_skills, node_embed, node_rank

# Build Graph
graph = StateGraph(ScreenerState)

# Add nodes
graph.add_node("extract_skills", node_extract_skills)
graph.add_node("embed", node_embed)
graph.add_node("rank", node_rank)

# Set entry point
graph.set_entry_point("extract_skills")

# Add edges connecting nodes
graph.add_edge("extract_skills", "embed")
graph.add_edge("embed", "rank")

# Set finish point
graph.set_finish_point("rank")

# Compile LangGraph App
app = graph.compile()

def run_screening(resume_texts: dict[str, str], jd_text: str) -> ScreenerState:
    """
    Initializes a new state with resumes and job description texts, 
    and invokes the langgraph compilation. 
    LangSmith auto-traces this automatically if LANGCHAIN_API_KEY is set in your environment.
    """
    # Build default state
    state = default_state()
    state["resume_texts"] = resume_texts
    state["jd_text"] = jd_text

    # Start the LangGraph execution
    result = app.invoke(state)
    
    return result
