import logging
import uuid
from contextlib import asynccontextmanager

from agent_framework import Agent, Message
from agent_framework.observability import create_resource, enable_instrumentation
from azure.monitor.opentelemetry import configure_azure_monitor
from pydantic import BaseModel

from fastapi import FastAPI
from maf.agent import create_agent
from maf.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Configure Azure Monitor first
if settings.appinsights_connection_string is not None:
    configure_azure_monitor(
        connection_string=settings.appinsights_connection_string.get_secret_value(),
        resource=create_resource(),  # Uses OTEL_SERVICE_NAME, etc.
        enable_live_metrics=True,
    )
else:
    logger.warning("no azure monitor enabled!")

# Then activate Agent Framework's telemetry code paths
# This is optional if ENABLE_INSTRUMENTATION and/or ENABLE_SENSITIVE_DATA are set in env vars
enable_instrumentation(enable_sensitive_data=settings.enable_sensitive_data)

sessions: dict[str, list[Message]] = {}
agent: Agent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    agent = create_agent()
    yield


app = FastAPI(title="MAF Chat Demo", lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    if agent is None:
        raise RuntimeError("Agent unset.")

    if body.session_id:
        session_id = body.session_id
    else:
        session_id = str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = [Message("user", body.message)]
    else:
        sessions[session_id].append(Message("user", body.message))

    result = await agent.run(sessions[session_id], session_id=session_id)
    sessions[session_id].append(Message("system", result.text))

    return ChatResponse(reply=result.text, session_id=session_id)
