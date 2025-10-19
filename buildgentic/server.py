import logging
import os
 
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from buildgentic.architect.agent import get_architect_agent, get_architect_agent_card
from buildgentic.compliance.agent import get_compliance_agent, get_compliance_agent_card
from buildgentic.developer.agent import get_developer_agent, get_developer_agent_card
from buildgentic.qa.agent import get_qa_agent, get_qa_agent_card

from .a2a_utils import A2AUtils

from buildgentic.manager.agent import (
    get_manager_agent,
    get_manager_agent_card,
)

 
load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


AGENT_BASE_URL = os.getenv("AGENT_BASE_URL")


if not AGENT_BASE_URL:
    raise ValueError("AGENT_BASE_URL environment variable must be set")


MODEL_NAME = os.getenv("MODEL_NAME")


if not MODEL_NAME:
    raise ValueError("MODEL_NAME environment variable must be set")
logger.info(f"AGENT BASE URL {AGENT_BASE_URL}")


app: FastAPI = FastAPI(
    title="Run multiple agents on single host using A2A protocol.",
    description="Run multiple agents on single host using A2A protocol.",
    version="1.0.0",
    root_path="/a2a",
)

 
@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
 
 
# conversation agent integration with A2A server
A2AUtils.build(
    name="manager",
    get_agent=get_manager_agent,
    get_agent_card=get_manager_agent_card,
    model_name=MODEL_NAME,
    agent_base_url=AGENT_BASE_URL,
    app=app,
)

A2AUtils.build(
    name="architect",
    get_agent=get_architect_agent,
    get_agent_card=get_architect_agent_card,
    model_name=MODEL_NAME,
    agent_base_url=AGENT_BASE_URL,
    app=app,
)

A2AUtils.build(
    name="developer",
    get_agent=get_developer_agent,
    get_agent_card=get_developer_agent_card,
    model_name=MODEL_NAME,
    agent_base_url=AGENT_BASE_URL,
    app=app,
)

A2AUtils.build(
    name="qa",
    get_agent=get_qa_agent,
    get_agent_card=get_qa_agent_card,
    model_name=MODEL_NAME,
    agent_base_url=AGENT_BASE_URL,
    app=app,
)

A2AUtils.build(
    name="compliance",
    get_agent=get_compliance_agent,
    get_agent_card=get_compliance_agent_card,
    model_name=MODEL_NAME,
    agent_base_url=AGENT_BASE_URL,
    app=app,
)

def run_server(host, port):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server("0.0.0.0", 8000)