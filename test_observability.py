import os
from dotenv import load_dotenv
load_dotenv()

from observability.langsmith_setup import configure_langsmith
from observability.logger import get_logger, log_screening_run

configure_langsmith()

print("LANGSMITH_TRACING  :", os.environ.get("LANGSMITH_TRACING"))
print("LANGSMITH_API_KEY  :", os.environ.get("LANGSMITH_API_KEY", "")[:8] + "...")
print("LANGSMITH_PROJECT  :", os.environ.get("LANGSMITH_PROJECT"))

logger = get_logger(__name__)
logger.info("Smoke test started", env="local")

log_screening_run(
    logger=logger,
    n_resumes=3,
    processing_time=1.42,
    top_score=0.87
)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(
    model=os.environ["LLM_MODEL"],
    openai_api_key=os.environ["OPENROUTER_API_KEY"],
    openai_api_base=os.environ["OPENROUTER_BASE_URL"],
)

response = llm.invoke([HumanMessage(content="Say: LangSmith trace working!")])
print("\nLLM Response:", response.content)
print("\n✅ Check smith.langchain.com → Projects → resume-iq for the trace")

# Smoke test script that configures LangSmith, verifies environment variables, emits a structured log, simulates a screening run, and sends a test LLM call to confirm tracing works end-to-end.