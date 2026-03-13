import uuid
from contextlib import asynccontextmanager

from agent_framework.observability import create_resource, enable_instrumentation
from azure.monitor.opentelemetry import configure_azure_monitor
from pydantic import BaseModel

from fastapi import FastAPI
from maf.agent import create_agent

# Configure Azure Monitor first
configure_azure_monitor(
    connection_string="InstrumentationKey=...",
    resource=create_resource(),  # Uses OTEL_SERVICE_NAME, etc.
    enable_live_metrics=True,
)

# Then activate Agent Framework's telemetry code paths
# This is optional if ENABLE_INSTRUMENTATION and/or ENABLE_SENSITIVE_DATA are set in env vars
enable_instrumentation(enable_sensitive_data=False)

threads: dict = {}
agent = None


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
    if body.session_id and body.session_id in threads:
        session_id = body.session_id
        thread = threads[session_id]
    else:
        session_id = str(uuid.uuid4())
        thread = agent.get_new_thread()

    result = await agent.run(body.message, thread=thread)
    threads[session_id] = thread

    return ChatResponse(reply=result.text, session_id=session_id)
