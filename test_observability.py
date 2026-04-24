import os
from dotenv import load_dotenv
load_dotenv()

from observability.langsmith_setup import configure_langsmith
from observability.logger import get_logger, log_screening_run

# Step 1: Boot LangSmith
configure_langsmith()

# Step 2: Confirm env vars are set
print("LANGSMITH_TRACING  :", os.environ.get("LANGSMITH_TRACING"))
print("LANGSMITH_API_KEY  :", os.environ.get("LANGSMITH_API_KEY", "")[:8] + "...")  # masked
print("LANGSMITH_PROJECT  :", os.environ.get("LANGSMITH_PROJECT"))

# Step 3: Fire a structured log
logger = get_logger(__name__)
logger.info("Smoke test started", env="local")

# Step 4: Simulate a screening run log
log_screening_run(
    logger=logger,
    n_resumes=3,
    processing_time=1.42,
    top_score=0.87
)

# Step 5: Fire a real LangChain call so a trace appears in LangSmith
from langchain_openai import ChatOpenAI  # works with openrouter too
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(
    model=os.environ["LLM_MODEL"],
    openai_api_key=os.environ["OPENROUTER_API_KEY"],
    openai_api_base=os.environ["OPENROUTER_BASE_URL"],
)

response = llm.invoke([HumanMessage(content="Say: LangSmith trace working!")])
print("\nLLM Response:", response.content)
print("\n✅ Check smith.langchain.com → Projects → resume-iq for the trace")