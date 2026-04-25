from langgraph.graph import StateGraph

from agents.state import ScreenerState, default_state
from agents.nodes import node_extract_skills, node_embed, node_rank

graph = StateGraph(ScreenerState)

graph.add_node("extract_skills", node_extract_skills)
graph.add_node("embed", node_embed)
graph.add_node("rank", node_rank)

graph.set_entry_point("extract_skills")

graph.add_edge("extract_skills", "embed")
graph.add_edge("embed", "rank")

graph.set_finish_point("rank")

app = graph.compile()

def run_screening(resume_texts: dict[str, str], jd_text: str) -> ScreenerState:
    """
    Initializes a new state with resumes and job description texts, 
    and invokes the langgraph compilation. 
    LangSmith auto-traces this automatically if LANGSMITH_API_KEY is set in your environment.
    """
    state = default_state()
    state["resume_texts"] = resume_texts
    state["jd_text"] = jd_text

    result = app.invoke(state)
    
    return result

# Defines and compiles the LangGraph screening pipeline with three sequential nodes: extract_skills → embed → rank. Provides `run_screening()` to execute the full pipeline on given resumes and a job description.
