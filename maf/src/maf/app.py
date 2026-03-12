import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from maf.agent import create_agent

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
