import os
from config import settings

def configure_langsmith() -> None:
    """
    Configures LangSmith environment variables to dynamically route execution
    traces directly to LangSmith for full lifecycle observability.
    Should be invoked once during the parent app startup sequence.
    """
    if settings.LANGSMITH_API_KEY:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT
        os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"

def get_run_url() -> str:
    """
    Returns the LangSmith project URL for easy logging and quick navigation
    to the trace dashboard.
    """
    project_name = settings.LANGSMITH_PROJECT
    return f"https://smith.langchain.com/projects/{project_name}"

def create_eval_dataset_entry(
    resume_name: str, 
    jd_snippet: str, 
    predicted_skills: list[str], 
    score: float
) -> dict:
    """
    Generates a structured dictionary record reflecting a single discrete screening prediction.
    
    NOTE ON EVALUATIONS: 
    For now, evaluations in this system are executed manually. The entries produced by this 
    function can be streamed out as JSONL or tabulated logs, then uploaded directly to the 
    LangSmith UI interface as a standalone Dataset. These static datasets can then be utilized 
    as robust baseline reference sets for executing automated, programmatic eval runs moving forward.
    """
    return {
        "inputs": {
            "resume_name": resume_name,
            "jd_snippet": jd_snippet
        },
        "outputs": {
            "predicted_skills": predicted_skills,
            "score": float(score)
        }
    }
