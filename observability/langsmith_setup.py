import os
from config import settings

def configure_langsmith() -> None:
    """
    Configures LangChain environment variables to dynamically route execution
    traces directly to LangSmith for full lifecycle observability.
    Should be invoked once during the parent app startup sequence.
    """
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT

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
